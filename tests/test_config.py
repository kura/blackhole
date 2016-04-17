import getpass
import grp
from io import StringIO
import os
import pytest
import unittest
from unittest import mock

from blackhole.config import Config, Singleton
from blackhole.exceptions import ConfigException


class FakeArgs(object):
    config_file = None


@mock.patch('getpass.getuser')
@mock.patch('grp.getgrgid')
def test_base(mock_getuser, mock_getgrgid):
    conf = Config()
    assert conf.config_file == '/etc/blackhole.conf'
    assert mock_getuser.called
    assert mock_getgrgid.called


@mock.patch('os.access', return_value=False)
def test_no_access(mock_os_access):
    conf = Config()
    conf.config_file = '/fake/file.conf'
    with pytest.raises(IOError):
        conf.load()


sample = """
#not=thisline
port=1025
address=10.0.0.1
this won't be added"""
@mock.patch('os.access', return_value=True)
@mock.patch('builtins.open', return_value=StringIO(sample))
def test_load(mock_os_access, mock_open):
    conf = Config().load()
    assert conf.port == 1025
    assert conf.address == '10.0.0.1'
    assert getattr(conf, 'not', None) is None
    assert getattr(conf, 'this', None) is None


class TestPort(unittest.TestCase):

    def setUp(self):
        Singleton._instances = {}

    @mock.patch('os.access', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO(''))
    def test_default_port(self, _, __):
        conf = Config().load()
        assert conf.port == 25

    sample = "port=xcbsfbsrwgrwgsgrsgsdgrwty4y4fsg"
    @mock.patch('os.access', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO(sample))
    def test_str_port(self, _, __):
        conf = Config().load()
        with pytest.raises(ConfigException):
            conf.test_port()

    sample = "port=19"
    @mock.patch('os.access', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO(sample))
    def test_valid_port(self, _, __):
        conf = Config().load()
        assert conf.port == 19

    sample = "port=0"
    @mock.patch('os.access', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO(sample))
    def test_lower_than_min(self, _, __):
        conf = Config().load()
        with pytest.raises(ConfigException):
            conf.test_port()

    sample = "port=99999"
    @mock.patch('os.access', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO(sample))
    def test_larger_than_max(self, _, __):
        conf = Config().load()
        with pytest.raises(ConfigException):
            conf.test_port()


class TestUser(unittest.TestCase):

    def setUp(self):
        Singleton._instances = {}

    sample = "user=xcbsfbsrwgrwgsgrsgsdgrwty4y4fsg"
    @mock.patch('os.access', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO(sample))
    def test_invalid_user(self, _, __):
        conf = Config().load()
        with pytest.raises(ConfigException):
            conf.test_user()

    sample = "user={}".format(getpass.getuser())
    @mock.patch('os.access', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO(sample))
    def test_valid_user(self, _, __):
        conf = Config().load()
        assert conf.user == getpass.getuser()


class TestGroup(unittest.TestCase):

    def setUp(self):
        Singleton._instances = {}

    sample = "group=xcbsfbsrwgrwgsgrsgsdgrwty4y4fsg"
    @mock.patch('os.access', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO(sample))
    def test_invalid_group(self, _, __):
        conf = Config().load()
        with pytest.raises(ConfigException):
            conf.self_test()

    sample = "group={}".format(grp.getgrgid(os.getgid()).gr_name)
    @mock.patch('os.access', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO(sample))
    def test_valid_group(self, _, __):
        conf = Config().load()
        assert conf.group == grp.getgrgid(os.getgid()).gr_name


class TestTimeout(unittest.TestCase):

    def setUp(self):
        Singleton._instances = {}

    @mock.patch('os.access', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO(''))
    def test_default_timeout(self, _, __):
        conf = Config().load()
        assert conf.timeout == 60

    sample = "timeout=xcbsfbsrwgrwgsgrsgsdgrwty4y4fsg"
    @mock.patch('os.access', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO(sample))
    def test_str_timeout(self, _, __):
        conf = Config().load()
        with pytest.raises(ConfigException):
            conf.test_timeout()

    sample = "timeout=10"
    @mock.patch('os.access', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO(sample))
    def test_str_timeout(self, _, __):
        conf = Config().load()
        assert conf.timeout == 10
