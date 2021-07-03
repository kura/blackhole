# -*- coding: utf-8 -*-

# (The MIT License)
#
# Copyright (c) 2013-2021 Kura
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
import pathlib
import pwd
import socket
import tempfile

from .exceptions import ConfigException
from .utils import Singleton, get_version, mailname


__all__ = ("parse_cmd_args", "warn_options", "config_test", "Config")
"""Tuple all the things."""


def parse_cmd_args(args):
    """
    Parse arguments from the command line.

    https://kura.gg/blackhole/configuration.html#command-line-options

    :param list args: Command line arguments.
    :returns: Parsed command line arguments.
    :rtype: :py:class:`argparse.Namespace`
    """
    ls_help = (
        "Disable ssl.OP_SINGLE_DH_USE and ssl.OP_SINGLE_ECDH_USE. "
        "Reduces CPU overhead at the expense of security -- Don't "
        "use this option unless you really need to."
    )

    description = (
        "Blackhole is an MTA (mail transfer agent) that "
        "(figuratively) pipes all mail to /dev/null. Blackhole is "
        "built on top of asyncio and utilises async def and await "
        "statements available in Python 3.5 and above."
    )

    epilog = (
        "An explanation of all command line and all configuration "
        "options is provided here -- "
        "https://kura.gg/blackhole/configuration.html"
    )

    parser = argparse.ArgumentParser(
        "blackhole",
        description=description,
        epilog=epilog,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=get_version(),
    )
    parser.add_argument(
        "-c",
        "--conf",
        type=str,
        dest="config_file",
        metavar="FILE",
        help="override the default configuration options",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-t",
        "--test",
        dest="test",
        action="store_true",
        help="perform a configuration test",
    )
    group.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        help="enable debugging mode",
    )
    group.add_argument(
        "-b",
        "--background",
        dest="background",
        action="store_true",
        help="run in the background",
    )
    group.add_argument(
        "-q",
        "--quiet",
        dest="quiet",
        action="store_true",
        help="Suppress warnings",
    )
    parser.add_argument(
        "-ls",
        "--less-secure",
        dest="less_secure",
        action="store_true",
        help=ls_help,
    )
    return parser.parse_args(args)


def warn_options(config):
    """
    Warn the user when using certain options.

    :param Config config: The configuration.
    """
    logger = logging.getLogger("blackhole.warnings")
    if config.args.less_secure:
        logger.warning(
            "Using -ls or --less-secure reduces security on "
            "SSL/TLS connections.",
        )
    if not config.tls_dhparams and len(config.tls_listen) > 0:
        logger.warning(
            "TLS is enabled but no Diffie Hellman ephemeral "
            "parameters file was provided.",
        )
    _compare_uid_and_gid(config)


def config_test(args):
    """
    Test the validity of the configuration file content.

    :param argparse.Namespace args: Parsed arguments.
    :raises SystemExit: Exit code :py:obj:`os.EX_OK` when config is valid
                        or :py:obj:`os.EX_USAGE` when config is invalid.

    .. note::

       Problems with the configuration will be written to the console using
       the :py:mod:`logging` module.
    """
    logger = logging.getLogger("blackhole.config.test")
    logger.setLevel(logging.INFO)
    try:
        conf = Config(args.config_file).load().test()
        conf.args = args
    except ConfigException:
        logger.critical("Config error")
        raise SystemExit(os.EX_USAGE)
    logger.info(f"blackhole: {args.config_file} syntax is OK.")
    logger.info(f"blackhole: {args.config_file} test was successful.")
    warn_options(conf)
    raise SystemExit(os.EX_OK)


def _compare_uid_and_gid(config):
    """
    Compare the current user and group and conf settings.

    :param Config config: The configuration.
    """
    logger = logging.getLogger("blackhole.warnings")
    uid, gid = os.getuid(), os.getgid()
    user, group = config.user, config.group
    if (uid == 0 and gid == 0) and (user == "root" and group == "root"):
        logger.warning(
            "It is unsafe to run Blackhole as root without setting "
            "a user and group for privilege separation.",
        )


class Config(metaclass=Singleton):
    """
    Configuration module.

    Default values are provided as well as self-test functionality
    to sanity check configuration.

    https://kura.gg/blackhole/configuration.html#configuration-options
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
    _pidfile = os.path.join(tempfile.gettempdir(), "blackhole.pid")
    _delay = None
    _mode = "accept"
    _max_message_size = 512000
    _dynamic_switch = None

    def __init__(self, config_file=None):
        """
        Initialise the configuration.

        :param str config_file: The configuration file path. Default: ``None``
        """
        if config_file:
            self.config_file = config_file
        self.user = getpass.getuser()
        self.group = grp.getgrgid(os.getgid()).gr_name
        # this has to be cached here due to the socket.getfqdn call failing
        # in os.fork
        self.mailname = mailname()

    def load(self):
        """
        Load the configuration file and parse.

        :raises ConfigException: When the configuration is invalid.
        :returns: :class:`Config`.

        .. note::

           Spaces, single and double quotes will be stripped. Lines beginning
           # will be ignored. # comments in-line will be stripped out and
           ignored.

           i.e.

           # listen = :1025, :::1025   ->
           listen = :25, :::25  # IPv4 & IPv6   ->   listen = :25, :::25
        """
        if self.config_file is None:
            return self
        if not os.access(self.config_file, os.R_OK):
            msg = "Config file does not exist or is not readable."
            raise ConfigException(msg)
        with open(self.config_file, "r") as _conf_file:
            for line in _conf_file.readlines():
                line = line.strip()
                if line.startswith("#"):
                    continue
                if line.strip() == "":
                    continue
                if "#" in line:
                    line = line.split("#")[0]
                if line.count("=") >= 1:
                    key, value = line.split("=", 1)
                    key, value = key.strip(), value.strip()
                    self.validate_option(key)
                    value = value.replace('"', "").replace("'", "")
                    setattr(self, key, value)
                else:
                    self.validate_option(line)
        return self

    def validate_option(self, key):
        """
        Validate config option is actually... valid...

        https://kura.gg/blackhole/configuration.html#configuration-options

        :param str key: Configuration option.
        :raises ConfigException: When an invalid option is configured.
        """
        if key == "":
            return
        attributes = inspect.getmembers(
            self,
            lambda a: not (inspect.isroutine(a)),
        )
        attrs = [
            a[0][1:]
            for a in attributes
            if not (a[0].startswith("__") and a[0].endswith("__"))
            and a[0].startswith("_")
        ]
        if key not in attrs:
            _attrs = "', '".join(attrs[:-1])
            valid_attrs = f"'{_attrs}' and '{attrs[-1]}'"
            msg = (
                f"Invalid configuration option '{key}'.\n\nValid options "
                f"are: {valid_attrs}"
            )
            raise ConfigException(msg)

    @property
    def workers(self):
        """
        How many workers to spawn to handle incoming connections.

        https://kura.gg/blackhole/configuration.html#workers

        :returns: Number of workers. Default: ``1``
        :rtype: :py:obj:`int`

        .. note::

           Default value is 1.

           A supervisor process will always exist separately from the workers.
        """
        return int(self._workers) or 1

    @workers.setter
    def workers(self, workers):
        self._workers = workers

    @property
    def listen(self):
        """
        Address, port and socket family.

        https://kura.gg/blackhole/configuration.html#listen

        :returns: Listeners.
        :rtype: :py:obj:`list`

        .. note::

           Default IPv4:

               [('127.0.0.1', 25, socket.AF_INET,
                ('127.0.0.1', 587, socket.AF_INET), ]

           Default IPv6:

               [('127.0.0.1', 25, socket.AF_INET),
                ('127.0.0.1', 587, socket.AF_INET), ]
        """
        ipv4 = [
            ("127.0.0.1", 25, socket.AF_INET, {}),
            ("127.0.0.1", 587, socket.AF_INET, {}),
        ]
        ipv6 = [
            ("::", 25, socket.AF_INET6, {}),
            ("::", 587, socket.AF_INET6, {}),
        ]
        default = ipv4 + ipv6 if socket.has_ipv6 else ipv4
        return self._listen or default

    @listen.setter
    def listen(self, addrs):
        self._listen = self._listeners(addrs)

    @property
    def tls_listen(self):
        """
        Address and port and socket family for SSL/TLS connections.

        https://kura.gg/blackhole/configuration.html#tls-listen

        :returns: TLS listeners. Default: ``[]``
        :rtype: :py:obj:`list`
        """
        return self._tls_listen or []

    @tls_listen.setter
    def tls_listen(self, addrs):
        self._tls_listen = self._listeners(addrs)

    @property
    def user(self):
        """
        UNIX user.

        https://kura.gg/blackhole/configuration.html#user

        :returns: User name.
        :rtype: :py:obj:`str`

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
        UNIX group.

        https://kura.gg/blackhole/configuration.html#group

        :returns: Group name.
        :rtype: :py:obj:`str`

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
        Timeout in seconds.

        https://kura.gg/blackhole/configuration.html#timeout

        :returns: Timeout in seconds. Default: ``60``
        :rtype: :py:obj:`int`

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
        TLS key file.

        https://kura.gg/blackhole/configuration.html#tls-key

        :returns: Path to a TLS key file. Default: ``None``
        :rtype: :py:obj:`str`
        """
        return self._tls_key

    @tls_key.setter
    def tls_key(self, tls_key):
        if tls_key is not None:
            self._tls_key = tls_key

    @property
    def tls_cert(self):
        """
        TLS certificate file.

        https://kura.gg/blackhole/configuration.html#tls-cert

        :returns: Path to a TLS certificate. Default: ``None``
        :rtype: :py:obj:`str`
        """
        return self._tls_cert

    @tls_cert.setter
    def tls_cert(self, tls_cert):
        if tls_cert is not None:
            self._tls_cert = tls_cert

    @property
    def tls_dhparams(self):
        """
        Diffie Hellman ephemeral parameters.

        https://kura.gg/blackhole/configuration.html#tls-dhparams

        :returns: Path to a file containing dhparams. Default: ``None``
        :rtype: :py:obj:`str`
        """
        return self._tls_dhparams

    @tls_dhparams.setter
    def tls_dhparams(self, tls_dhparams):
        if tls_dhparams is not None:
            self._tls_dhparams = tls_dhparams

    @property
    def pidfile(self):
        """
        Path to store the pid.

        https://kura.gg/blackhole/configuration.html#pidfile

        :returns: Path to a pid file. Default: ``/tmp/blackhole.pid``.
        :rtype: :py:obj:`str`
        """
        return self._pidfile

    @pidfile.setter
    def pidfile(self, pidfile):
        if pidfile is not None:
            self._pidfile = pidfile

    @property
    def delay(self):
        """
        Delay in seconds.

        https://kura.gg/blackhole/configuration.html#delay

        :returns: Delay in seconds. Default: ``None``
        :rtype: :py:obj:`int` or :py:obj:`None`

        .. note::

           Defaults to :py:obj:`None`.
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
        Mode with which to respond.

        https://kura.gg/blackhole/configuration.html#mode

        :returns: A response mode. Default: ``accept``.
        :rtype: :py:obj:`str`

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
        Maximum size, in bytes, of a message.

        https://kura.gg/blackhole/configuration.html#max-message-size

        :returns: Maximum message size in bytes. Default: ``512000``.
        :rtype: :py:obj:`int`

        .. note::

           Default 512000 bytes (512 KB).
        """
        if self._max_message_size is not None:
            return int(self._max_message_size)
        return None

    @max_message_size.setter
    def max_message_size(self, size):
        self._max_message_size = size

    @property
    def dynamic_switch(self):
        """
        Enable or disable dynamic switches.

        https://kura.gg/blackhole/configuration.html#dynamic-switch

        :returns: Whether dynamic switches are enabled or not. Default:
                  ``True``.
        :rtype: :py:obj:`bool`

        .. note::

           Allowed values are :py:obj:`True` and :py:obj:`False`.
           Default: :py:obj:`True`
        """
        if self._dynamic_switch is None:
            return True
        return self._dynamic_switch

    @dynamic_switch.setter
    def dynamic_switch(self, switch):
        if switch.lower() == "false":
            self._dynamic_switch = False
        elif switch.lower() == "true":
            self._dynamic_switch = True
        else:
            msg = f"{switch} is not valid. Options are true or false."
            raise ConfigException(msg)

    def _convert_port(self, port):
        """
        Convert a port from the configuration files' string to an integer.

        :param str port: A port number.
        :type port: :py:obj:`str`
        :raises ConfigException: If an invalid port number if provided.
        :returns: A port number.
        :rtype: :py:obj:`int`
        """
        try:
            return int(port)
        except ValueError:
            msg = f"{port} is not a valid port number."
            raise ConfigException(msg)

    def _listeners(self, listeners):
        """
        Convert listeners lines from the configuration to usable values.

        :param str listeners: A list of addresses and ports, separated by
                              commas.
                              -- e.g. '127.0.0.1:25, 10.0.0.1:25, :25, :::25'
        :returns: List of addresses and sockets to listen on.
        :rtype: :py:obj:`list` or :py:obj:`None`
        """
        clisteners = []
        _listeners = listeners.split(",")
        if len(_listeners) == 0:
            return None
        for listener in _listeners:
            listener = listener.strip()
            parts = listener.split(" ")
            addr_port = parts[0]
            port = addr_port.split(":")[-1].strip()
            addr = addr_port.replace(f":{port}", "").strip()
            family = socket.AF_INET
            if ":" in addr:
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

        :param str addr: The listener host address.
        :param int port: The listener port.
        :returns: Flags defined for this socket. Default: ``{}``.
        :rtype: :py:obj:`dict`

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
        if addr in ("127.0.0.1", "0.0.0.0"):  # nosec
            addr = ""
        elif addr in ("::1",):
            addr = "::"
        listeners = self.listen + self.tls_listen
        for laddr, lport, __, lflags in listeners:
            if laddr == addr and lport == port:
                return lflags
        return {}

    def create_flags(self, parts):
        """
        Create a set of flags from a listener directive.

        :param list parts: Parts of the listener definition.
        :returns: Flags for a listener. Default: ``{}``.
        :rtype: :py:obj:`dict`
        """
        flags = {}
        for part in parts:
            if part.count("=") == 1:
                flag, value = part.split("=")
                flag, value = flag.strip(), value.strip()
                if flag in ("mode", "delay"):
                    if flag == "mode":
                        flags.update(self._flag_mode(flag, value))
                    elif flag == "delay":
                        flags.update(self._flag_delay(flag, value))
        return flags

    def _flag_mode(self, flag, value):
        """
        Create a flag for the mode directive.

        :param str flag: The flag name.
        :param str value: The value of the flag.
        :returns: Mode flag for a listener.
        :rtype: :py:obj:`dict`
        :raises ConfigException: If an invalid mode is provided.
        """
        if value in ("accept", "bounce", "random"):
            return {flag: value}
        else:
            raise ConfigException(
                f"'{value}' is not a valid mode. Valid options "
                "are: 'accept', 'bounce' and 'random'.",
            )

    def _flag_delay(self, flag, value):
        """
        Create a delay flag, delay can be an int or a range.

        :param str flag: The flag name.
        :param str value: The value of the flag.
        :returns: Delay flag for a listener.
        :rtype: :py:obj:`dict`
        :raises ConfigException: If an invalid delay is provided.
        """
        if value.count("-") == 0:
            if value.isdigit() and int(value) < 60:
                return {flag: value}
            else:
                raise ConfigException(
                    f"'{value}' is not a valid delay. Delay is "
                    "in seconds and must be below 60.",
                )
        if value.count("-") == 1:
            start, end = value.split("-")
            start, end = start.strip(), end.strip()
            if (
                start.isdigit()
                and end.isdigit()
                and int(start) < 60
                and int(end) < 60
                and int(end) > int(start)
            ):
                return {flag: (start, end)}
        raise ConfigException(
            f"'{value}' is not a valid delay value. It must be "
            "either a single value or a range i.e. 5-10 and "
            "must be less than 60.",
        )

    def test(self):
        r"""
        Test configuration validity.

        :returns: The configuration object.
        :rtype: :class:`Config`

        .. note::

           Uses the magic of :py:func:`inspect.getmembers` to introspect
           methods beginning with \'test\_\' and calling them.
        """
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        for name, _ in members:
            if name.startswith("test_"):
                getattr(self, name)()
        return self

    def test_workers(self):
        """
        Validate the number of workers.

        :raises ConfigException: If an invalid number of workers is provided.

        .. note::

           Cannot have more workers than number of processors or cores.
        """
        cpus = multiprocessing.cpu_count()
        if self.workers > cpus:
            msg = (
                "Cannot have more workers than number of processors or "
                f"cores. {self.workers} workers > {cpus} processors/cores."
            )
            raise ConfigException(msg)

    def test_ipv6_support(self):
        """
        If an IPv6 listener is configured, confirm IPv6 is supported.

        :raises ConfigException: If IPv6 is configured but is not supported by
                                 the operating system.
        """
        for address, __, family, ___ in self.listen:
            if ":" in address:
                if not socket.has_ipv6 and family == socket.AF_UNSPEC:
                    msg = (
                        "An IPv6 listener is configured but IPv6 is not "
                        "available on this platform."
                    )
                    raise ConfigException(msg)

    def test_tls_ipv6_support(self):
        """
        If an IPv6 listener is configured, confirm IPv6 is supported.

        :raises ConfigException: If IPv6 is configured but is not supported by
                                 the operating system.
        """
        for address, __, family, ___ in self.tls_listen:
            if ":" in address:
                if not socket.has_ipv6 and family == socket.AF_UNSPEC:
                    msg = (
                        "An IPv6 listener is configured but IPv6 is not "
                        "available on this platform."
                    )
                    raise ConfigException(msg)

    def test_same_listeners(self):
        """
        Test that multiple listeners are not configured on the same port.

        :raises ConfigException: When multiple listeners are configured on the
                                 same port.

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
            msg = (
                "Cannot have multiple listeners on the same address and "
                "port."
            )
            raise ConfigException(msg)

    def test_no_listeners(self):
        """
        Test that at least one listener is configured.

        :raises ConfigException: When no listeners are configured.
        """
        if not len(self.listen) > 0 and not len(self.tls_listen) > 0:
            msg = "You need to define at least one listener."
            raise ConfigException(msg)

    def _min_max_port(self, port):
        """
        Minimum and maximum allowed port.

        :param int port: The port to test for validity.
        :raises ConfigException: When port is outside of the allowed range.

        .. note::

           On Linux the minimum is 1 and maximum is 65535.
        """
        min_port, max_port = 1, 65535
        if port < min_port:
            msg = (
                f"Port number {port} is not usable because it is less than "
                f"{min_port} which is the lowest available port."
            )
            raise ConfigException(msg)
        if port > max_port:
            msg = (
                f"Port number {port} is not usable because it is less than "
                f"{max_port} which is the highest available port."
            )
            raise ConfigException(msg)

    def test_port(self):
        """
        Validate port number.

        :raises ConfigException: When a port is configured that we have no
                                 permissions for.
        """
        for host, port, family, __ in self.listen:
            self._port_permissions(host, port, family)

    def _port_permissions(self, address, port, family):
        """
        Validate that we have permission to use the port and it's not in use.

        :param str address: The address to use.
        :param int port: The port to use.
        :param family: The type of socket to use.
        :type family: :py:obj:`socket.AF_INET` or :py:obj:`socket.AF_INET6`
        :raises ConfigException: When a port is supplied that we have no
                                 permissions for.
        """
        self._min_max_port(port)
        if os.getuid() != 0 and port < 1024:
            msg = f"You do not have permission to use port {port}"
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
            errmsg = err.strerror
            msg = f"Could not use port {port}, {errmsg}"
            raise ConfigException(msg)
        finally:
            sock.close()
            del sock

    def test_user(self):
        """
        Validate user exists in UNIX password database.

        :raises ConfigException: When the user cannot be accessed on the
                                 operating system.

        .. note::

           Defaults to :py:func:`getpass.getuser` if no user is specified.
        """
        try:
            pwd.getpwnam(self.user)
        except KeyError:
            msg = f"{self._user} is not a valid user."
            raise ConfigException(msg)

    def test_group(self):
        """
        Validate group exists in UNIX group database.

        :raises ConfigException: When the group cannot be accessed on the
                                 operating system.

        .. note::

           Defaults to :py:attr:`grp.getgrgid.gr_name` if no group is
           specified.
        """
        try:
            grp.getgrnam(self.group)
        except KeyError:
            msg = f"{self._group} is a not a valid group."
            raise ConfigException(msg)

    def test_timeout(self):
        """
        Validate timeout - only allow a valid integer value in seconds.

        :raises ConfigException: When the timeout is not a number or is above
                                 the maximum allowed value of 180.
        """
        try:
            __ = self.timeout  # NOQA
        except ValueError:
            msg = f"{self._timeout} is not a valid number of seconds."
            raise ConfigException(msg)
        if self.timeout and self.timeout > 180:
            msg = (
                "Timeout must be at least 180 seconds or less for security "
                "(denial of service)."
            )
            raise ConfigException(msg)

    def test_tls_port(self):
        """
        Validate TLS port number.

        :raises ConfigException: When a port is configured that we have no
                                 permissions for.
        """
        if len(self.tls_listen) == 0:
            return
        for host, port, af, __ in self.tls_listen:
            self._port_permissions(host, port, af)

    def test_tls_settings(self):
        """
        Validate TLS configuration.

        :raises ConfigException: When the TLS configuration is invalid.

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
            msg = (
                "To use TLS you must supply a port, certificate file "
                "and key file."
            )
            raise ConfigException(msg)

    def test_tls_dhparams(self):
        """
        Validate Diffie Hellman ephemeral parameters.

        :raises ConfigException: When the dhparams file is invalid.

        .. note::

           Verifies Diffie Hellman ephemeral parameters are readable.
        """
        if self.tls_dhparams and not os.access(self.tls_dhparams, os.R_OK):
            msg = (
                "To use Diffie Hellman ephemeral params you must supply a "
                "valid dhparams file."
            )
            raise ConfigException(msg)

    def test_delay(self):
        """
        Validate the delay period.

        :raises ConfigException: When the delay is not a number or is above
                                 the maximum allowed value of 60.

        .. note::

           Delay must be lower than the timeout.
        """
        if self.delay and self.delay >= self.timeout:
            msg = "Delay must be lower than timeout."
            raise ConfigException(msg)
        if self.delay and self.delay > 60:
            msg = (
                "Delay must be 60 seconds or less for security (denial of "
                "service)."
            )
            raise ConfigException(msg)

    def test_mode(self):
        """
        Validate the response mode.

        :raise ConfigException: When an invalid mode is configured.

        .. note::

           Valid options are: 'accept', 'bounce' and 'random'.
        """
        if self.mode not in ("accept", "bounce", "random"):
            msg = "Mode must be accept, bounce or random."
            raise ConfigException(msg)

    def test_max_message_size(self):
        """
        Validate max_message size is an integer.

        :raise ConfigException: When the maximum message size is not a number.
        """
        try:
            __ = self.max_message_size  # NOQA
        except ValueError:
            size = self._max_message_size
            msg = f"{size} is not a valid number of bytes."
            raise ConfigException(msg)

    def test_pidfile(self):
        """
        Validate that the pidfile can be written to.

        :raises ConfigException: When the pidfile is invalid.
        """
        if not self.pidfile:
            return
        pidfile = pathlib.Path(self.pidfile)
        if not os.access(pidfile.parent, os.W_OK):
            msg = "You do not have permission to write to the pidfile."
            raise ConfigException(msg)

    def test_dynamic_switch(self):
        """
        Validate that the dynamic_switch value is correct.

        :raises ConfigException: When the dynamic switch value is invalid.
        """
        if self._dynamic_switch is None:
            return
        if self._dynamic_switch not in (True, False):
            msg = "Allowed dynamic_switch values are true and false."
            raise ConfigException(msg)
