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

"""Configuration structure."""


import argparse
import getpass
import grp
import inspect
import logging
import os
import pwd
import re
import socket

from blackhole.exceptions import ConfigException


__version__ = __import__('blackhole').__version__


def parse_cmd_args(args):
    """
    Parse arguments from the command line.

    :param args:
    :type args: list
    """
    parser = argparse.ArgumentParser('blackhole')
    parser.add_argument('-v', '--version', action='version',
                        version=__version__)
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
    return parser.parse_args(args)


def config_test(args):
    """
    Test the validity of the configuration file content.

    .. note::

       Problems with the configuration will be written to the console using
       the `logging` module.

       Calls `sys.exit` upon an error.

    :param args: arguments parsed from `argparse`.
    :type args: `argparse.Namespace`
    """
    logger = logging.getLogger('blackhole.config_test')
    logger.setLevel(logging.INFO)
    try:
        conf = Config(args.config_file).load().test()
    except ConfigException as err:
        logger.fatal(err)
        raise SystemExit(os.EX_USAGE)
    logger.info('blackhole: %s syntax is OK', args.config_file)
    logger.info('blackhole: %s test was successful', args.config_file)
    if len(conf.tls_listen) > 0 and not conf.tls_dhparams:
        logger.warn('TLS is enabled but no Diffie Hellman phemeral parameters '
                    'file was provided.')
    raise SystemExit(os.EX_OK)


class Singleton(type):
    """A singleton for `blackhole.config.Config`."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """A singleton for `blackhole.config.Config`."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]


class Config(metaclass=Singleton):
    """
    Configuration module.

    Default values are provided as well as self-test functionality
    to sanity check configuration.
    """

    config_file = None
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
        :type config_file: str
        """
        self.config_file = config_file
        self.user = getpass.getuser()
        self.group = grp.getgrgid(os.getgid()).gr_name

    def load(self):
        """
        Load the configuration file and parse.

        Spaces, single and double quotes will be stripped. Lines beginning in
        # will be ignored.

        :returns: obj -- An instance of `blackhole.config.Config`
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
            try:
                key, value = line.split('=')
            except ValueError:
                continue
            key, value = key.strip(), value.strip()
            value = value.replace('"', '').replace("'", '')
            setattr(self, key, value)
        return self

    @property
    def listen(self):
        """
        Addresses and ports to listen on.

        .. note::

            Default value is 127.0.0.1:25
        """
        return self._listen or [('127.0.0.1', 25, socket.AF_INET)]

    @listen.setter
    def listen(self, addrs):
        self._listen = self._listeners(addrs)

    def _convert_port(self, port):
        """
        Convert a port from the configuration files' string to an integer.

        :raises: ConfigException
        """
        try:
            _ = int(port)
        except ValueError:
            raise ConfigException('Cannot convert {} to an '
                                  'integer'.format(port))
        return int(port)

    def _listeners(self, addresses):
        """
        Convert listener lines from the configuration to usable values.

        :param addresses:
        :type addresses: str -- e.g. '127.0.0.1:25, 10.0.0.1:25'
        :returns: list or None
        """
        addrs = []
        _addrs = addresses.split(',')
        if len(_addrs) == 0:
            return
        for addr in _addrs:
            port = addr.split(':')[-1].strip()
            name = addr.replace(':{}'.format(port), '').strip()
            af = socket.AF_INET
            if ':' in name:
                af = socket.AF_INET6
            host = (name, self._convert_port(port), af)
            addrs.append(host)
        return addrs

    @property
    def tls_listen(self):
        """
        Addresses and ports to listen on for SSL/TLS connections
        """
        return self._tls_listen or []

    @tls_listen.setter
    def tls_listen(self, addrs):
        self._tls_listen = self._listeners(addrs)

    @property
    def user(self):
        """
        A UNIX user.

        .. note::

           Defaults to the current user.

        :returns: str -- A UNIX user.
        """
        return self._user

    @user.setter
    def user(self, user):
        self._user = user

    @property
    def group(self):
        """
        A UNIX group.

        .. note::

           Defaults to the current group.

        :returns: str -- A UNIX group.
        """
        return self._group

    @group.setter
    def group(self, group):
        self._group = group

    @property
    def timeout(self):
        """
        A timeout in seconds.

        .. note::

           Defaults to 60 seconds.
           Cannot be more 180 seconds for security (denial of service).

        :returns: int -- A timeout in seconds.
        """
        return int(self._timeout)

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout

    @property
    def tls_key(self):
        """
        A TLS key file.

        :returns: str
        """
        return self._tls_key

    @tls_key.setter
    def tls_key(self, tls_key):
        self._tls_key = tls_key

    @property
    def tls_cert(self):
        """
        A TLS certificate file.

        :returns: str
        """
        return self._tls_cert

    @tls_cert.setter
    def tls_cert(self, tls_cert):
        self._tls_cert = tls_cert

    @property
    def tls_dhparams(self):
        """
        Diffie Hellman ephemeral parameters.

        :returns: str
        """
        return self._tls_dhparams

    @tls_dhparams.setter
    def tls_dhparams(self, tls_dhparams):
        self._tls_dhparams = tls_dhparams

    @property
    def pidfile(self):
        """
        A path to store the pid.

        :returns: str -- A filesystem path.
        """
        return self._pidfile

    @pidfile.setter
    def pidfile(self, pidfile):
        self._pidfile = pidfile

    @property
    def delay(self):
        """
        A delay in seconds.

        .. note::

           Defaults to None.
           Cannot be higher than 60 seconds for security (denial of service).

        :returns: int or None -- A delay in seconds.
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

        .. note::

           Defaults to 'accept'.
           Options: 'accept', 'bounce' and 'random'.

        :returns: str -- The server response mode.
        """
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode = mode.lower()

    @property
    def max_message_size(self):
        """
        The maximum size, in bytes, of a message.

        .. note::

           Default 512000 bytes (512 KB).
        :returns: int
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

        .. note::

           Allowed values are true and false.
           Default: true
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
            raise ConfigException(''''{}' is not valid. Options are true or '''
                                  '''false'''.format(switch))

    def test(self):
        """
        Test configuration validity.

        .. note::

           Uses the magic of `inspect.getmembers` to introspect methods
           beginning with 'test_' and calling them.

        :returns: obj -- An instance of `blackhole.config.Config`.
        """
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        for name, _ in members:
            if name.startswith('test_'):
                getattr(self, name)()
        return self

    def test_same_listeners(self):
        """
        Test that multiple listeners are not configured on the same port.

        .. note::

           IPv4 and IPv6 addresses are different sockets so they can listen on
           the same port because they have different addresses.
        """
        if len(self.listen) == 0 and len(self.tls_listen) == 0:
            return
        if set(self.listen).intersection(self.tls_listen):
            raise ConfigException('Cannot have multiple listeners on the same'
                                  'host and port')

    def test_no_listeners(self):
        """Test that at least one listener is configured."""
        if not len(self.listen) > 0 and not len(self.tls_listen) > 0:
            raise ConfigException('You need to define at least one listener')

    def _min_max_port(self, port):
        """
        The minimum and maximum allowed port.

        :param port: The port.
        :type port: int
        :raises: `blackhole.config.ConfigException`

        .. note::

           On Linux the minimum is 1 and maximum is 65535.
        """
        min_port, max_port = 1, 65535
        if port < min_port:
            msg = ('Port number {} is not usable because it is less than '
                   '{} which is the lowest available port.').format(port,
                                                                    min_port)
            raise ConfigException(msg)
        if port > max_port:
            msg = ('Port number {} is not usable because it is less than '
                   '{} which is the highest available port').format(port,
                                                                    max_port)
            raise ConfigException(msg)

    def test_port(self):
        """
        Validate port number.

        :raises: `blackhole.exceptions.ConfigException`
        """
        for host, port, af in self.listen:
            self._port_permissions(host, port, af)

    def _port_permissions(self, host, port, af):
        """
        Validate that we have permission to use the port and it's not in use.

        :param port:
        :type port: int
        :raises: ConfigException
        """
        self._min_max_port(port)
        if os.getuid() is not 0 and port < 1024:
            msg = 'You do not have permission to use port {}'.format(port)
            raise ConfigException(msg)
        sock = socket.socket(af, socket.SOCK_STREAM)
        try:
            sock.bind((host, port))
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

        :raises: `blackhole.exceptions.ConfigException`

        .. note::

           Defaults to `getpass.getuser` if no user is specified.
        """
        try:
            pwd.getpwnam(self.user)
        except KeyError:
            msg = '{} is not a valid user.'.format(self._user)
            raise ConfigException(msg)

    def test_group(self):
        """
        Validate group exists in UNIX group database.

        :raises: `blackhole.exceptions.ConfigException`

        .. note::

           Defaults to `grp.getgrgid.gr_name` if no group is specified.
        """
        try:
            grp.getgrnam(self.group)
        except KeyError:
            msg = '{} is a not a valid group.'.format(self._group)
            raise ConfigException(msg)

    def test_timeout(self):
        """
        Validate timeout - only allow a valid integer value in seconds.

        :raises: `blackhole.exceptions.ConfigException`
        """
        try:
            _ = self.timeout
        except ValueError:
            msg = '{} is not a valid number of seconds.'.format(self._timeout)
            raise ConfigException(msg)
        if self.timeout and self.timeout > 180:
            raise ConfigException('Timeout must be 180 seconds or less for '
                                  'security (denial of service).')

    def test_tls_port(self):
        """
        Validate TLS port number.

        :raises: `blackhole.exceptions.ConfigException`
        """
        if len(self.tls_listen) == 0:
            return
        for host, port, af in self.tls_listen:
            self._port_permissions(host, port, af)

    def test_tls_settings(self):
        """
        Validate TLS configuration.

        :raises: `blackhole.exceptions.ConfigException`

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

        :raises: `blackhole.exceptions.ConfigException`

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

        Delay must be lower than the timeout.

        :raises: `blackhole.config.ConfigException`
        """
        if self.delay and self.delay >= self.timeout:
            raise ConfigException('Delay must be lower than timeout.')
        if self.delay and self.delay > 60:
            raise ConfigException('Delay must be 60 seconds or less for '
                                  'security (denial of service).')

    def test_mode(self):
        """
        Validate the response mode.

        Valid options are: 'accept', 'bounce' and 'random'.

        :raises: `blackhole.config.ConfigException`
        """
        if self.mode not in ('accept', 'bounce', 'random'):
            raise ConfigException('Mode must be accept, bounce or random.')

    def test_max_message_size(self):
        """
        Validate max_message size is an integer.

        :raises: `blackhole.exceptions.ConfigException`
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

        :raises: `blackhole.exceptions.ConfigException`
        """
        if not self.pidfile:
            return
        try:
            open(self.pidfile, 'w+')
        except PermissionError:
            msg = ('You do not have permission to write to the pidfile.')
            raise ConfigException(msg)
        except FileNotFoundError:
            msg = ('The path to the pidfile does not exist.')
            raise ConfigException(msg)

    def test_dynamic_switch(self):
        """
        Validate that the dynamic_switch value is correct.

        :raises: `blackhole.exceptions.ConfigException`
        """
        if self._dynamic_switch is None:
            return
        if self._dynamic_switch not in ('true', 'false'):
            raise ConfigException('Allowed dynamic_switch values are true and '
                                  'false.')
