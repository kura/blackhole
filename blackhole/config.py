# (The MIT License)
#
# Copyright (c) 2016 Kura
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Configuration structure and functionality for testing config validity."""


import argparse
import getpass
import grp
import inspect
import logging
import multiprocessing
import os
import pwd
import socket

from .exceptions import ConfigException
from .utils import mailname, get_version


__all__ = ('parse_cmd_args', 'warn_options', 'config_test', 'Config')


def parse_cmd_args(args):
    """
    Parse arguments from the command line.

    https://blackhole.io/command-line-options.html

    :param args: A list of option command line arguments.
    :type args: :any:`list`
    :returns: Parsed command line arguments.
    :rtype: :any:`argparse.Namespace`
    """
    ls_help = ('Disable ssl.OP_SINGLE_DH_USE and ssl.OP_SINGLE_ECDH_USE. '
               'Reduces CPU overhead at the expense of security -- Don\'t '
               'use this option unless you really need to.')

    decription = ('Blackhole is an MTA (mail transfer agent) that '
                  '(figuratively) pipes all mail to /dev/null. Blackhole is '
                  'built on top of asyncio and utilises async def and await '
                  'statements available in Python 3.5 and above.')

    epilog = ('An explanation of all command line arguments is provided here '
              '-- https://blackhole.io/command-line-options.html and all '
              'configuration options here -- '
              'https://blackhole.io/configuration-options.html.')

    parser = argparse.ArgumentParser('blackhole', description=decription,
                                     epilog=epilog)
    parser.add_argument('-v', '--version', action='version',
                        version=get_version())
    parser.add_argument('-c', '--conf', type=str,
                        default='/etc/blackhole.conf',
                        dest='config_file', metavar='/etc/blackhole.conf',
                        help='override the default configuration options')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-t', '--test', dest='test', action='store_true',
                       help='perform a configuration test')
    group.add_argument('-d', '--debug', dest='debug', action='store_true',
                       help='enable debugging mode')
    group.add_argument('-b', '--background', dest='background',
                       action='store_true',
                       help='run in the background')
    group.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                       help='Supress warnings')
    parser.add_argument('-ls', '--less-secure', dest='less_secure',
                        action='store_true', help=ls_help)
    return parser.parse_args(args)


def warn_options(config):
    """
    Warn the user when using certain options.

    :param config: The configuration.
    :type config: :any:`blackhole.config.Config`
    """
    logger = logging.getLogger('blackhole.warnings')
    if config.args.less_secure:
        logger.warning('Using -ls or --less-secure reduces security on '
                       'SSL/TLS connections.')
    if not config.tls_dhparams and len(config.tls_listen) > 0:
        logger.warning('TLS is enabled but no Diffie Hellman ephemeral '
                       'parameters file was provided.')
    _compare_uid_and_gid(config)


def config_test(args):
    """
    Test the validity of the configuration file content.

    :param args: arguments parsed from :any:`argparse`.
    :type args: :any:`argparse.Namespace`
    :raises: :any:`SystemExit` -- :any:`os.EX_USAGE` and :any:`os.EX_OK`

    .. note::

       Problems with the configuration will be written to the console using
       the :any:`logging` module.
    """
    logger = logging.getLogger('blackhole.config.test')
    logger.setLevel(logging.INFO)
    try:
        conf = Config(args.config_file).load().test()
        conf.args = args
    except ConfigException as err:
        logger.fatal(err)
        raise SystemExit(os.EX_USAGE)
    logger.info('blackhole: %s syntax is OK.', args.config_file)
    logger.info('blackhole: %s test was successful.', args.config_file)
    warn_options(conf)
    raise SystemExit(os.EX_OK)


def _compare_uid_and_gid(config):
    """
    Compare the current user and group and conf settings.

    :param config: The configuration.
    :type config: :any:`blackhole.config.Config`
    """
    logger = logging.getLogger('blackhole.warnings')
    uid, gid = os.getuid(), os.getgid()
    user, group = config.user, config.group
    if (uid == 0 and gid == 0) and (user == 'root' and group == 'root'):
        logger.warning('It is unsafe to run Blackhole as root without setting '
                       'a user and group for privilege revocation.')


class Singleton(type):
    """A singleton for :any:`blackhole.config.Config`."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """A singleton for :any:`blackhole.config.Config`."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]


class Config(metaclass=Singleton):
    """
    Configuration module.

    Default values are provided as well as self-test functionality
    to sanity check configuration.

    https://blackhole.io/configuration-options.html
    """

    args = None
    """Arguments parsed from the command line."""

    config_file = None
    """A file containing configuration values."""

    _workers = 1
    _listen = []
    _tls_listen = []
    _user = None
    _group = None
    _timeout = 60
    _tls_key = None
    _tls_cert = None
    _tls_dhparams = None
    _pidfile = '/tmp/blackhole.pid'
    _delay = None
    _mode = 'accept'
    _max_message_size = 512000
    _dynamic_switch = None

    def __init__(self, config_file="/etc/blackhole.conf"):
        """
        Initialise the configuration.

        :param config_file: The configuration file,
                            default '/etc/blackhole.conf'
        :type config_file: :any:`str`
        """
        self.config_file = config_file
        self.user = getpass.getuser()
        self.group = grp.getgrgid(os.getgid()).gr_name
        # this has to be cached here due to the socket.getfqdn call failing
        # in os.fork
        self.mailname = mailname()

    def load(self):
        """
        Load the configuration file and parse.

        :raises: :any:`blackhole.exceptions.ConfigException`
        :returns: An instance of :any:`blackhole.config.Config`
        :rtype: :any:`blackhole.config.Config`

        .. note::

           Spaces, single and double quotes will be stripped. Lines beginning
           # will be ignored. # comments in-line will be stripped out and
           ignored.

           i.e.

           listen = :25, :::25  # IPv4 & IPv6   ->   listen = :25, :::25
        """
        if self.config_file is None:
            return self
        if not os.access(self.config_file, os.R_OK):
            msg = 'Config file does not exist or is not readable.'
            raise ConfigException(msg)
        for line in open(self.config_file, 'r').readlines():
            line = line.strip()
            if line.startswith('#'):
                continue
            if '#' in line:
                line = line.split('#')[0]
            if line.count('=') >= 1:
                key, value = line.split('=', 1)
                key, value = key.strip(), value.strip()
                value = value.replace('"', '').replace("'", '')
                setattr(self, key, value)
        return self

    @property
    def workers(self):
        """
        Number of workers to spawn to handle incoming connections.

        https://blackhole.io/configuration-options.html#workers

        :returns: Number of workers.
        :rtype: :any:`int`

        .. note::

           Default value is 1.

           A supervisor process will always exist separately from the workers.
        """
        return int(self._workers)

    @workers.setter
    def workers(self, workers):
        self._workers = workers

    @property
    def listen(self):
        """
        Address, port and socket family.

        https://blackhole.io/configuration-options.html#listen

        :returns: Sockets to listen on.
        :rtype: :any:`list`

        .. note::

            Default value is [('127.0.0.1', 25, :any:`socket.AF_INET`),
                              ('127.0.0.1', 587, :any:`socket.AF_INET`)]
        """
        return self._listen or [('127.0.0.1', 25, socket.AF_INET, {}),
                                ('127.0.0.1', 587, socket.AF_INET, {})]

    @listen.setter
    def listen(self, addrs):
        self._listen = self._listeners(addrs)

    @property
    def tls_listen(self):
        """
        Address and port and socket family for SSL/TLS connections.

        https://blackhole.io/configuration-options.html#tls_listen

        :returns: Sockets to listen on.
        :rtype: :any:`list`
        """
        return self._tls_listen or []

    @tls_listen.setter
    def tls_listen(self, addrs):
        self._tls_listen = self._listeners(addrs)

    @property
    def user(self):
        """
        A UNIX user.

        https://blackhole.io/configuration-options.html#user

        :returns: A user name.
        :rtype: :any:`str`

        .. note::

           Defaults to the current user.
        """
        return self._user

    @user.setter
    def user(self, user):
        self._user = user

    @property
    def group(self):
        """
        A UNIX group.

        https://blackhole.io/configuration-options.html#group

        :returns: A group name.
        :rtype: :any:`str`

        .. note::

           Defaults to the current group.
        """
        return self._group

    @group.setter
    def group(self, group):
        self._group = group

    @property
    def timeout(self):
        """
        A timeout in seconds.

        https://blackhole.io/configuration-options.html#timeout

        :returns: A timeout in seconds.
        :rtype: :any:`int`

        .. note::

           Defaults to 60 seconds.
           Cannot be more 180 seconds for security (denial of service).
        """
        return int(self._timeout)

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout

    @property
    def tls_key(self):
        """
        A TLS key file.

        https://blackhole.io/configuration-options.html#tls_key

        :returns: A path to a TLS key file.
        :rtype: :any:`str`
        """
        return self._tls_key

    @tls_key.setter
    def tls_key(self, tls_key):
        self._tls_key = tls_key

    @property
    def tls_cert(self):
        """
        A TLS certificate file.

        https://blackhole.io/configuration-options.html#tls_cert

        :returns: A path to a TLS certificate.
        :rtype: :any:`str`
        """
        return self._tls_cert

    @tls_cert.setter
    def tls_cert(self, tls_cert):
        self._tls_cert = tls_cert

    @property
    def tls_dhparams(self):
        """
        Diffie Hellman ephemeral parameters.

        https://blackhole.io/configuration-options.html#tls_dhparams

        :returns: A path to a file containing dhparams.
        :rtype: :any:`str`
        """
        return self._tls_dhparams

    @tls_dhparams.setter
    def tls_dhparams(self, tls_dhparams):
        self._tls_dhparams = tls_dhparams

    @property
    def pidfile(self):
        """
        A path to store the pid.

        https://blackhole.io/configuration-options.html#pidfile

        :returns: A path to a pid file.
        :rtype: :any:`str`
        """
        return self._pidfile

    @pidfile.setter
    def pidfile(self, pidfile):
        self._pidfile = pidfile

    @property
    def delay(self):
        """
        A delay in seconds.

        https://blackhole.io/configuration-options.html#delay

        :returns: A delay in seconds or none if not configured.
        :rtype: :any:`int` or :any:`None`

        .. note::

           Defaults to :any:`None`.
           Cannot be higher than 60 seconds for security (denial of service).
        """
        if self._delay is not None:
            return int(self._delay)
        return None

    @delay.setter
    def delay(self, delay):
        self._delay = delay

    @property
    def mode(self):
        """
        The mode with which to respond.

        https://blackhole.io/configuration-options.html#mode

        :returns: A response mode.
        :rtype: :any:`str`

        .. note::

           Defaults to 'accept'.
           Options: 'accept', 'bounce' and 'random'.
        """
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode = mode.lower()

    @property
    def max_message_size(self):
        """
        The maximum size, in bytes, of a message.

        https://blackhole.io/configuration-options.html#max_message_size

        :returns: Maximum message size in bytes.
        :rtype: :any:`int`

        .. note::

           Default 512000 bytes (512 KB).
        """
        if self._max_message_size is not None:
            return int(self._max_message_size)

    @max_message_size.setter
    def max_message_size(self, size):
        self._max_message_size = size

    @property
    def dynamic_switch(self):
        """
        Enable or disable dynamic switches.

        https://blackhole.io/configuration-options.html#dynamic_switch

        :returns: Whether dynamic switches are enabled or not.
        :rtype: :any:`bool` - :any:`True` or :any:`False`

        .. note::

           Allowed values are :any:`True` and :any:`False`.
           Default: :any:`True`
        """
        if self._dynamic_switch is None:
            return True
        return self._dynamic_switch

    @dynamic_switch.setter
    def dynamic_switch(self, switch):
        if switch.lower() == 'false':
            self._dynamic_switch = False
        elif switch.lower() == 'true':
            self._dynamic_switch = True
        else:
            msg = '{} is not valid. Options are true or false.'.format(switch)
            raise ConfigException(msg)

    def _convert_port(self, port):
        """
        Convert a port from the configuration files' string to an integer.

        :param port: A port number.
        :type port: :any:`str`
        :raises: :any:`blackhole.exceptions.ConfigException`
        :returns: A port number.
        :rtype: :any:`int`
        """
        try:
            return int(port)
        except ValueError:
            msg = '{} is not a valid port number.'.format(port)
            raise ConfigException(msg)

    def _listeners(self, listeners):
        """
        Convert listeners lines from the configuration to usable values.

        :param listeners: A list of addresses and ports, separated by commas.
                         -- e.g. '127.0.0.1:25, 10.0.0.1:25, :25, :::25'
        :type listeners: :any:`str`
        :returns: A list of addresses and sockets to listen on.
        :rtype: :any:`list` or :any:`None`
        """
        clisteners = []
        _listeners = listeners.split(',')
        if len(_listeners) == 0:
            return
        for listener in _listeners:
            listener = listener.strip()
            parts = listener.split(' ')
            addr_port = parts[0]
            port = addr_port.split(':')[-1].strip()
            addr = addr_port.replace(':{}'.format(port), '').strip()
            family = socket.AF_INET
            if ':' in addr:
                family = socket.AF_INET6
            flags = {}
            if len(parts) > 1:
                flags = self.create_flags(parts[1:])
            host = (addr, self._convert_port(port), family, flags)
            clisteners.append(host)
        return clisteners

    def flags_from_listener(self, addr, port):
        """
        Get a list of flags defined for the provided listener.

        Scope: ``listen``, ``tls_listen``.

        :param addr: The listener host address.
        :type addr: :any:`str`
        :param port: The listener port.
        :type port: :any:`int`
        :returns: Flags defined for this socket.
        :rtype: :any:`dict`

        .. note::

           If multiple modes or delays are listed in a single listener, the
           last definition will be used:

           ``listen = :25 mode=bounce mode=random``  ->  ``mode=random``

           A mode and delay can be used in tandum:

           ``listen = :25 mode=bounce delay=10``

           The delay can also be specified as a range:

           ``listen = :25 delay=5-10``

           Using a delay range will cause the server to choose a random value
           within that range per connection.

           Mode and delay can be defined for each address/port in a listen
           directive:

           ``listen = :25 mode=bounce, :::25 delay=10, :587 mode=random``
        """
        if addr in ('127.0.0.1', '0.0.0.0'):
            addr = ''
        elif addr in ('::1', ):
            addr = '::'
        listeners = self.listen + self.tls_listen
        for laddr, lport, lfam, lflags in listeners:
            if laddr == addr and lport == port:
                return lflags
        return {}

    def create_flags(self, parts):
        """
        Create a set of flags from a listener directive.

        :param parts: Parts of the listener definition.
        :type parts: :any:`list`
        :returns: Flags for a listener.
        :rtype: :any:`dict`
        """
        flags = {}
        for part in parts:
            if part.count('=') == 1:
                flag, value = part.split('=')
                flag, value = flag.strip(), value.strip()
                if flag in ('mode', 'delay'):
                    if flag == 'mode':
                        flags.update(self._flag_mode(flag, value))
                    elif flag == 'delay':
                        flags.update(self._flag_delay(flag, value))
        return flags

    def _flag_mode(self, flag, value):
        """
        Create a flag for the mode directive.

        :param flag: The flag name.
        :type flag: :any:`str`
        :param value: The value of the flag.
        :type value: :any:`str`
        :returns: Mode flag for a listener.
        :rtype: :any:`dict`
        :raises: :any:`blackhole.exception.ConfigException`
        """
        if value in ('accept', 'bounce', 'random'):
            return {flag: value}
        else:
            raise ConfigException('\'{}\' is not a valid mode. Valid options '
                                  'are: \'accept\', \'bounce\' and '
                                  '\'random\'.'.format(value))

    def _flag_delay(self, flag, value):
        """
        Create a delay flag, delay can be an int or a range.

        :param flag: The flag name.
        :type flag: :any:`str`
        :param value: The value of the flag.
        :type value: :any:`str`
        :returns: Delay flag for a listener.
        :rtype: :any:`dict`
        :raises: :any:`blackhole.exception.ConfigException`
        """
        if value.count('-') == 0:
            if value.isdigit() and int(value) < 60:
                return {flag: value}
            else:
                raise ConfigException('\'{}\' is not a valid delay. Delay is '
                                      'in seconds and must be below '
                                      '60.'.format(value))
        if value.count('-') == 1:
            start, end = value.split('-')
            start, end = start.strip(), end.strip()
            if start.isdigit() and end.isdigit() and int(start) < 60 and \
                    int(end) < 60 and int(end) > int(start):
                return {flag: (start, end)}
        raise ConfigException('\'{}\' is not a valid delay value. It must be '
                              'either a single value or a range i.e. 5-10 and '
                              'must be less than 60.'.format(value))

    def test(self):
        """
        Test configuration validity.

        :returns: An instance of :any:`blackhole.config.Config`.
        :rtype: :any:`blackhole.config.Config`

        .. note::

           Uses the magic of :any:`inspect.getmembers` to introspect methods
           beginning with 'test_' and calling them.
        """
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        for name, _ in members:
            if name.startswith('test_'):
                getattr(self, name)()
        return self

    def test_workers(self):
        """
        Validate the number of workers.

        :raises: :any:`blackhole.exceptions.ConfigException`

        .. note::

           Cannot have more workers than number of processors or cores.
        """
        cpus = multiprocessing.cpu_count()
        if self.workers > cpus:
            msg = ('Cannot have more workers than number of processors or '
                   'cores. {} workers > {} processors/cores.')
            msg.format(self.workers, cpus)
            raise ConfigException(msg)

    def test_ipv6_support(self):
        """
        If an IPv6 listener is configured, confirm IPv6 is supported.

        :raises: :any:`blackhole.exceptions.ConfigException`
        """
        for address, port, family, flags in self.listen:
            if ':' in address:
                if not socket.has_ipv6 and family == socket.AF_UNSPEC:
                    msg = ('An IPv6 listener is configured but IPv6 is not '
                           'available on this platform.')
                    raise ConfigException(msg)

    def test_tls_ipv6_support(self):
        """
        If an IPv6 listener is configured, confirm IPv6 is supported.

        :raises: :any:`blackhole.exceptions.ConfigException`
        """
        for address, port, family, flags in self.tls_listen:
            if ':' in address:
                if not socket.has_ipv6 and family == socket.AF_UNSPEC:
                    msg = ('An IPv6 listener is configured but IPv6 is not '
                           'available on this platform.')
                    raise ConfigException(msg)

    def test_same_listeners(self):
        """
        Test that multiple listeners are not configured on the same port.

        :raises: :any:`blackhole.exceptions.ConfigException`

        .. note::

           IPv4 and IPv6 addresses are different sockets so they can listen on
           the same port because they have different addresses.
        """
        if len(self.listen) == 0 and len(self.tls_listen) == 0:
            return
        listen, tls_listen = [], []
        for llisten in self.listen:
            addr, port, family, flags = llisten
            listen.append((addr, port, family))
        for llisten in self.tls_listen:
            addr, port, family, flags = llisten
            tls_listen.append((addr, port, family))
        if set(listen).intersection(tls_listen):
            msg = ('Cannot have multiple listeners on the same address and '
                   'port.')
            raise ConfigException(msg)

    def test_no_listeners(self):
        """
        Test that at least one listener is configured.

        :raises: :any:`blackhole.exceptions.ConfigException`
        """
        if not len(self.listen) > 0 and not len(self.tls_listen) > 0:
            msg = 'You need to define at least one listener.'
            raise ConfigException(msg)

    def _min_max_port(self, port):
        """
        The minimum and maximum allowed port.

        :param port: The port to test for validity.
        :type port: :any:`int`
        :raises: :any:`blackhole.exceptions.ConfigException`

        .. note::

           On Linux the minimum is 1 and maximum is 65535.
        """
        min_port, max_port = 1, 65535
        if port < min_port:
            msg = ('Port number {} is not usable because it is less than '
                   '{} which is the lowest available port.')
            msg.format(port, min_port)
            raise ConfigException(msg)
        if port > max_port:
            msg = ('Port number {} is not usable because it is less than '
                   '{} which is the highest available port.')
            msg.format(port, max_port)
            raise ConfigException(msg)

    def test_port(self):
        """
        Validate port number.

        :raises: :any:`blackhole.exceptions.ConfigException`
        """
        for host, port, family, flags in self.listen:
            self._port_permissions(host, port, family)

    def _port_permissions(self, address, port, family):
        """
        Validate that we have permission to use the port and it's not in use.

        :param address: The address to use.
        :type address: :any:`str`
        :param port: The port to use.
        :type port: :any:`int`
        :param family: The type of socket to use.
        :type family: :any:`socket.AF_INET` or :any:`socket.AF_INET6`
        :raises: :any:`blackhole.exceptions.ConfigException`
        """
        self._min_max_port(port)
        if os.getuid() is not 0 and port < 1024:
            msg = 'You do not have permission to use port {}'.format(port)
            raise ConfigException(msg)
        sock = socket.socket(family, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except (AttributeError, OSError):
            pass
        if family == socket.AF_INET6:
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        try:
            sock.bind((address, port))
        except OSError as err:
            errmsg = err.strerror.lower()
            msg = 'Could not use port {}, {}'.format(port, errmsg)
            raise ConfigException(msg)
        finally:
            sock.close()
            del sock

    def test_user(self):
        """
        Validate user exists in UNIX password database.

        :raises: :any:`blackhole.exceptions.ConfigException`

        .. note::

           Defaults to :any:`getpass.getuser` if no user is specified.
        """
        try:
            pwd.getpwnam(self.user)
        except KeyError:
            msg = '{} is not a valid user.'.format(self._user)
            raise ConfigException(msg)

    def test_group(self):
        """
        Validate group exists in UNIX group database.

        :raises: :any:`blackhole.exceptions.ConfigException`

        .. note::

           Defaults to :any:`grp.getgrgid.gr_name` if no group is specified.
        """
        try:
            grp.getgrnam(self.group)
        except KeyError:
            msg = '{} is a not a valid group.'.format(self._group)
            raise ConfigException(msg)

    def test_timeout(self):
        """
        Validate timeout - only allow a valid integer value in seconds.

        :raises: :any:`blackhole.exceptions.ConfigException`
        """
        try:
            _ = self.timeout
        except ValueError:
            msg = '{} is not a valid number of seconds.'.format(self._timeout)
            raise ConfigException(msg)
        if self.timeout and self.timeout > 180:
            msg = ('Timeout must be 180 seconds or less for security (denial '
                   'of service).')
            raise ConfigException(msg)

    def test_tls_port(self):
        """
        Validate TLS port number.

        :raises: :any:`blackhole.exceptions.ConfigException`
        """
        if len(self.tls_listen) == 0:
            return
        for host, port, af, flags in self.tls_listen:
            self._port_permissions(host, port, af)

    def test_tls_settings(self):
        """
        Validate TLS configuration.

        :raises: :any:`blackhole.exceptions.ConfigException`

        .. note::

           Verifies if you provide all TLS settings, not just some.
        """
        port = True
        if not len(self.tls_listen) > 0:
            port = False
        cert = os.access(self.tls_cert, os.R_OK) if self.tls_cert else False
        key = os.access(self.tls_key, os.R_OK) if self.tls_key else False
        if (port, cert, key) == (False, False, False):
            return
        if not all((port, cert, key)):
            msg = ('To use TLS you must supply a port, certificate file '
                   'and key file.')
            raise ConfigException(msg)

    def test_tls_dhparams(self):
        """
        Validate Diffie Hellman ephemeral parameters.

        :raises: :any:`blackhole.exceptions.ConfigException`

        .. note::

           Verifies Diffie Hellman ephemeral parameters are readable.
        """
        if self.tls_dhparams and not os.access(self.tls_dhparams, os.R_OK):
            msg = ('To use Diffie Hellman ephemeral params you must supply a '
                   'valid dhparams file.')
            raise ConfigException(msg)

    def test_delay(self):
        """
        Validate the delay period.

        :raises: :any:`blackhole.exceptions.ConfigException`

        .. note::

           Delay must be lower than the timeout.
        """
        if self.delay and self.delay >= self.timeout:
            msg = 'Delay must be lower than timeout.'
            raise ConfigException(msg)
        if self.delay and self.delay > 60:
            msg = ('Delay must be 60 seconds or less for security (denial of '
                   'service).')
            raise ConfigException(msg)

    def test_mode(self):
        """
        Validate the response mode.

        :raises: :any:`blackhole.exceptions.ConfigException`

        .. note::

           Valid options are: 'accept', 'bounce' and 'random'.
        """
        if self.mode not in ('accept', 'bounce', 'random'):
            msg = 'Mode must be accept, bounce or random.'
            raise ConfigException(msg)

    def test_max_message_size(self):
        """
        Validate max_message size is an integer.

        :raises: :any:`blackhole.exceptions.ConfigException`
        """
        try:
            _ = self.max_message_size
        except ValueError:
            size = self._max_message_size
            msg = '{} is not a valid number of bytes.'.format(size)
            raise ConfigException(msg)

    def test_pidfile(self):
        """
        Validate that the pidfile can be written to.

        :raises: :any:`blackhole.exceptions.ConfigException`
        """
        if not self.pidfile:
            return
        try:
            open(self.pidfile, 'w+')
        except PermissionError:
            msg = 'You do not have permission to write to the pidfile.'
            raise ConfigException(msg)
        except FileNotFoundError:
            msg = 'The path to the pidfile does not exist.'
            raise ConfigException(msg)

    def test_dynamic_switch(self):
        """
        Validate that the dynamic_switch value is correct.

        :raises: :any:`blackhole.exceptions.ConfigException`
        """
        if self._dynamic_switch is None:
            return
        if self._dynamic_switch not in ('true', 'false'):
            msg = 'Allowed dynamic_switch values are true and false.'
            raise ConfigException(msg)
