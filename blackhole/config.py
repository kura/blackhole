# -*- coding: utf-8 -*-

import getpass
import grp
import inspect
import os
import pwd
import re

from blackhole.exceptions import ConfigException


class Config(object):
    address = '127.0.0.1'
    port = 25
    config_file = None
    user = None
    group = None
    log_file = None
    timeout = 60

    def __init__(self, config_file="/etc/blackhole.conf"):
        self.config_file = config_file
        self.user, self.group = getpass.getuser(), getpass.getuser()

    def load(self):
        if not os.access(self.config_file, os.R_OK):
            raise IOError("Config file does not exist or is not readable.")
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
            if not getattr(self, key):
                continue
            setattr(self, key.strip(), value.strip())
        return True

    def self_test(self):
        """
        Test configuration validity.

        Note:
            Should be called after `Config.load`.

        Example:

            >>> config blackhole.config.Config('/etc/blackhole.conf')
            >>> config.load()
            >>> config.test()
        """
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        for member in members:
            name, mcallable = member
            if name.startswith('test_'):
                mcallable()

    def test_address(self):
        address = re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", self.address)
        if self.address not in ('localhost',):
            msg = "{} is not a valid IPv4 address".format(self.address)
            raise ConfigException(msg)

    def test_port(self):
        try:
            int(self.port)
        except ValueError:
            msg = "{} is not a valid port number".format(self.port)
            raise ConfigException(msg)

    def test_user(self):
        try:
            pwd.getpwnam(self.user)
        except ValueError:
            msg = "{} is not a valid user".format(self.user)
            raise ConfigException(msg)

    def test_group(self):
        try:
            grp.getgrnam(self.group)
        except ValueError:
            msg = "{} is a not a valid group".format(self.group)
            raise ConfigException(msg)

    def test_log_file(self):
        if self.log_file is not None and not os.access(self.log_file, os.W_OK):
            msg = "Cannot open log file {} for writing".format(self.log_file)
            raise ConfigException(msg)
