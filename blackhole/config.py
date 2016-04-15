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

"""Configuration structure for Blackhole."""


import getpass
import grp
import inspect
import os
import pwd
import re

from blackhole.exceptions import ConfigException


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
    Configuration module for Blackhole.

    Default values are provided as well as self-test functionality
    to sanity check configuration.
    """

    config_file = None
    _address = '127.0.0.1'
    _port = 25
    _user = None
    _group = None
    _log_file = None
    _timeout = 60
    _tls_port = None
    _tls_key = None
    _tls_cert = None

    def __init__(self, config_file="/etc/blackhole.conf"):
        """
        Initialise the configuration.

        Set the default user and group to the current user and group from
        `getpass.getuser`.

        :param config_file: The configuration file,
                            default '/etc/blackhole.conf'
        :type config_file: str
        """
        self.config_file = config_file
        self.user, self.group = getpass.getuser(), getpass.getuser()

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
            raise IOError('Config file does not exist or is not readable.')
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
    def address(self):
        return self._address

    @property
    def port(self):
        """
        A port number.

        :returns: int -- A port number.
        """
        return int(self._port)

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def user(self):
        """
        A UNIX user.

        .. note::

           Defaults to the current user using `getpass.getuser`.

        :returns: str -- A UNIX user.
        """
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def group(self):
        """
        A UNIX group.

        .. note::

           Defaults to a group named after the current user
           from `getpass.getuser`, assumes a group exists that is named after
           the current user.

        :returns: str -- A UNIX group.
        """
        return self._group

    @group.setter
    def group(self, value):
        self._group = value

    @property
    def log_file(self):
        """
        A full file path.

        :returns: str -- A full file path.
        """
        return self._log_file

    @log_file.setter
    def log_file(self, value):
        self._log_file = value

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
    def timeout(self, value):
        self._timeout = value

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
    def tls_port(self, value):
        self._tls_port = value

    @property
    def tls_key(self):
        """
        A TLS key file.

        :returns: str
        """
        return self._tls_key

    @tls_key.setter
    def tls_key(self, value):
        self._tls_key = value

    @property
    def tls_cert(self):
        """
        A TLS certificate file.

        :returns: str
        """
        return self._tls_cert

    @tls_cert.setter
    def tls_cert(self, value):
        self._tls_cert = value

    def self_test(self):
        """Test configuration validity.

        .. notes::

           Uses the magic of `inspect.getmembers` to introspect methods
           beginning with 'test_' and calling them.

        :returns: obj -- An instance of `blackhole.config.Config`.
        """
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        for member in members:
            name, mcallable = member
            if name.startswith('test_'):
                mcallable()
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
            msg = '{} is not a valid IPv4 address.'.format(self.address)
            raise ConfigException(msg)

    def test_port(self):
        """
        Validate port number.

        :raises: `blackhole.exceptions.ConfigException`

        .. note::

           Only verifies port is a valid integer, does not verify port is
           available or not in use.
        """
        try:
            int(self.port)
        except ValueError:
            msg = '{} is not a valid port number.'.format(self.port)
            raise ConfigException(msg)

    def test_user(self):
        """
        Validate user exists in UNIX password database.

        :raises: `blackhole.exceptions.ConfigException`

        .. note::

           Defaults to `getpass.getuser` if no user is specified.
        """
        try:
            pwd.getpwnam(self.user)
        except ValueError:
            msg = '{} is not a valid user.'.format(self.user)
            raise ConfigException(msg)

    def test_group(self):
        """
        Validate group exists in UNIX group database.

        :raises: `blackhole.exceptions.ConfigException`

        .. note::

           Defaults to `getpass.getuser` if no group is specified. Assumes a
           group has been created with the same name as the user.
        """
        try:
            grp.getgrnam(self.group)
        except ValueError:
            msg = '{} is a not a valid group.'.format(self.group)
            raise ConfigException(msg)

    def test_log_file(self):
        """
        Validate log file and location are writable.

        :raises: `blackhole.exceptions.ConfigException`
        """
        if self.log_file is not None and not os.access(self.log_file, os.W_OK):
            msg = 'Cannot open log file {} for writing.'.format(self.log_file)
            raise ConfigException(msg)

    def test_timeout(self):
        """
        Validate timeout - only allow a valid integer value in seconds.

        :raises: `blackhole.exceptions.ConfigException`
        """
        try:
            int(self.timeout)
        except ValueError:
            msg = '{} is not a valid number of seconds.'.format(self.timeout)
            raise ConfigException(msg)

    def test_tls_port(self):
        """
        Validate TLS port number.

        :raises: `blackhole.exceptions.ConfigException`

        .. note::

           Only verifies port is a valid integer, does not verify port is
           available or not in use.
        """
        if self._tls_port is None:
            return
        try:
            int(self.tls_port)
        except ValueError:
            msg = '{} is not a valid port number.'.format(self.tls_port)
            raise ConfigException(msg)
        if self.port == self.tls_port:
            raise ConfigException("SMTP and SMTP/TLS ports must be different.")

    def test_tls_settings(self):
        """
        Validate TLS configuration.

        :raises: `blackhole.exceptions.ConfigException`

        .. note::

           Verifies that if you provide all TLS settings, not just some.
        """
        port = self.tls_port if self.tls_port is not None else False
        cert = os.access(self.tls_cert, os.R_OK) if self.tls_cert else False
        key = os.access(self.tls_key, os.R_OK) if self.tls_key else False
        if (port, cert, key) == (False, False, False):
            return
        if not all((port, cert, key)):
            msg = 'To use TLS you must supply a port, certificate file and key file.'
            raise ConfigException(msg)
