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
    parser = argparse.ArgumentParser('blackhole')
    parser.add_argument('-c', '--conf', type=str,
                        default='/etc/blackhole.conf',
                        dest='config_file', metavar='/etc/blackhole.conf',
                        help='override the default configuration options')
    parser.add_argument('-v', '--version', action='version',
                        version=__version__)
    parser.add_argument('-t', '--test', dest='test', action='store_true',
                        help='perform a configuration test and exit')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help='enable debugging mode')
    parser.add_argument('-b', '--background', dest='background',
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
        Config(args.config_file).load().test()
    except ConfigException as err:
        logger.fatal(err)
        raise SystemExit(os.EX_USAGE)
    logger.info('blackhole: %s syntax is OK', args.config_file)
    logger.info('blackhole: %s test was successful', args.config_file)
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
    _address = '127.0.0.1'
    _port = 25
    _user = None
    _group = None
    # _log_file = None
    _timeout = 60
    _tls_port = None
    _tls_key = None
    _tls_cert = None
    _pidfile = '/tmp/blackhole.pid'
    _delay = None
    _mode = 'accept'
    _max_message_size = 512000

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
            key = "_{}".format(key)
            value = value.replace('"', '').replace("'", '')
            setattr(self, key, value)
        return self

    @property
    def address(self):
        """
        An IPv4 address.

        :returns: str -- IPv4 address.
        """
        return self._address

    @address.setter
    def address(self, address):
        self._address = address

    @property
    def port(self):
        """
        A port number.

        :returns: int -- A port number.
        """
        return int(self._port)

    @port.setter
    def port(self, port):
        self._port = port

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

    # @property
    # def log_file(self):
    #     """
    #     A full file path.
    #
    #     :returns: str -- A full file path.
    #     """
    #     return self._log_file
    #
    # @log_file.setter
    # def log_file(self, value):
    #     self._log_file = value

    @property
    def timeout(self):
        """
        A timeout in seconds.

        .. note::

           Defaults to 60 seconds.

        :returns: int -- A timeout in seconds.
        """
        return int(self._timeout)

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout

    @property
    def tls_port(self):
        """
        A port number.

        :returns: int
        """
        if self._tls_port is None:
            return None
        return int(self._tls_port)

    @tls_port.setter
    def tls_port(self, tls_port):
        self._tls_port = tls_port

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

        :returns: int or None -- A timeout in seconds.
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

    def test_address(self):
        """
        Validate IPv4 address format.

        :raises: `blackhole.exceptions.ConfigException`

        .. note::

           Classifies 'localhost' as a valid IPv4 address.
        """
        address = re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", self.address)
        if self.address not in ('localhost',) and not address:
            msg = '{} is not a valid IPv4 address.'.format(self._address)
            raise ConfigException(msg)

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
        try:
            _ = self.port
        except ValueError:
            msg = '{} is not a valid port number.'.format(self._port)
            raise ConfigException(msg)
        self._port_permissions(self.port)

    def _port_permissions(self, port):
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
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('127.0.0.1', port))
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

    # def test_log_file(self):
    #     """
    #     Validate log file and location are writable.
    #
    #     :raises: `blackhole.exceptions.ConfigException`
    #     """
    #     if self.log_file is not None and not os.access(self.log_file, os.W_OK):
    #         msg = 'Cannot open log file {} for writing.'.format(self.log_file)
    #         raise ConfigException(msg)

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

    def test_tls_port(self):
        """
        Validate TLS port number.

        :raises: `blackhole.exceptions.ConfigException`
        """
        if self._tls_port is None:
            return
        try:
            _ = self.tls_port
        except ValueError:
            msg = '{} is not a valid port number.'.format(self._tls_port)
            raise ConfigException(msg)
        if self.port == self.tls_port:
            raise ConfigException('SMTP and SMTP/TLS ports must be different.')
        self._port_permissions(self.tls_port)

    def test_tls_settings(self):
        """
        Validate TLS configuration.

        :raises: `blackhole.exceptions.ConfigException`

        .. note::

           Verifies if you provide all TLS settings, not just some.
        """
        port = self.tls_port if self.tls_port is not None else False
        cert = os.access(self.tls_cert, os.R_OK) if self.tls_cert else False
        key = os.access(self.tls_key, os.R_OK) if self.tls_key else False
        if (port, cert, key) == (False, False, False):
            return
        if not all((port, cert, key)):
            msg = ('To use TLS you must supply a port, certificate file '
                   'and key file.')
            raise ConfigException(msg)

    def test_delay(self):
        """
        Validate the delay period.

        Delay must be lower than the timeout.

        :raises: `blackhole.config.ConfigException`
        """
        if self.delay and self.delay >= self.timeout:
            raise ConfigException('Delay must be lower than timeout.')

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
