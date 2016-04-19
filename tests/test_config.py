import getpass
import grp
import os
import pytest
import random
import tempfile
import unittest
from unittest import mock

from blackhole.config import Config, Singleton, config_test, parse_cmd_args
from blackhole.exceptions import ConfigException


@pytest.fixture()
def cleandir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)


@pytest.fixture()
def reset_conf():
    Singleton._instances = {}


pytest.mark.usefixtures('reset_conf')
def create_config(data):
    cwd = os.getcwd()
    path = os.path.join(cwd, 'test.conf')
    with open(path, 'w') as cfile:
        cfile.write('\n'.join(data))
    return path


@mock.patch('getpass.getuser')
@mock.patch('grp.getgrgid')
@pytest.mark.usefixtures('reset_conf')
def test_default(mock_getuser, mock_getgrgid):
    conf = Config()
    assert conf.config_file == '/etc/blackhole.conf'
    assert mock_getuser.called is True
    assert mock_getuser.call_count is 1
    assert mock_getgrgid.called is True
    assert mock_getgrgid.call_count is 1


@pytest.mark.usefixtures('reset_conf')
@mock.patch('os.access', return_value=False)
def test_no_access(mock_os_access):
    conf = Config()
    conf.config_file = '/fake/file.conf'
    with pytest.raises(ConfigException):
        conf.load()
    assert mock_os_access.called is True
    assert mock_os_access.call_count is 1


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_load():
    cfile = create_config(('#not=thisline', 'port=1025', 'address=10.0.0.1',
                           '''this won't be added'''))

    conf = Config(cfile).load()
    assert conf.port == 1025
    assert conf.address == '10.0.0.1'
    assert getattr(conf, 'not', None) is None
    assert getattr(conf, 'this', None) is None


pytest.mark.usefixtures('reset_conf')
class TestCmdParser(unittest.TestCase):

    def test_default_conf(self):
        parser = parse_cmd_args(['-c/fake/file.conf'])
        assert parser.config_file == '/fake/file.conf'
        parser = parse_cmd_args(['--conf=/fake/file.conf'])
        assert parser.config_file == '/fake/file.conf'

    def test_version(self):
        with pytest.raises(SystemExit) as exc:
            parse_cmd_args(['-v'])
        assert str(exc.value) == '0'
        with pytest.raises(SystemExit) as exc:
            parse_cmd_args(['--version'])
        assert str(exc.value) == '0'

    def test_test(self):
        parser = parse_cmd_args(['-t'])
        assert parser.test is True
        parser = parse_cmd_args(['--test'])
        assert parser.test is True

    def test_debug(self):
        parser = parse_cmd_args(['-d'])
        assert parser.debug is True
        parser = parse_cmd_args(['--debug'])
        assert parser.debug is True

    def test_background(self):
        parser = parse_cmd_args(['-b'])
        assert parser.background is True
        parser = parse_cmd_args(['--background'])
        assert parser.background is True


class TestConfigTest(unittest.TestCase):

    class Args(object):
        pass

    def create_file(self, name):
        cwd = os.getcwd()
        path = os.path.join(cwd, name)
        with open(path, 'w') as ffile:
            ffile.write('nothing')
        return path

    @pytest.mark.usefixtures('reset_conf', 'cleandir')
    def test_config_test(self):
        key = self.create_file('key.key')
        cert = self.create_file('crt.crt')
        user = getpass.getuser()
        group = grp.getgrgid(os.getgid()).gr_name
        settings = ('address=0.0.0.0', 'port=1025', 'user={}'.format(user),
                    'group={}'.format(group), 'timeout=300', 'tls_port=1465',
                    'tls_cert={}'.format(cert), 'tls_key={}'.format(key),
                    'delay=10', 'mode=bounce')
        cfile = create_config(settings)
        args = self.Args()
        args.config_file = cfile
        with pytest.raises(SystemExit) as exc:
            config_test(args)
        assert str(exc.value) == '0'


@pytest.mark.usefixtures('reset_conf', 'cleandir')
class TestAddress(unittest.TestCase):

    def test_default(self):
        cfile = create_config(('',))
        conf = Config(cfile).load()
        assert conf.address == '127.0.0.1'

    def test_localhost(self):
        cfile = create_config(('address=localhost',))
        conf = Config(cfile).load()
        assert conf.address == 'localhost'

    def test_invalid(self):
        cfile = create_config(('address=blackhole.io',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_address()
        assert conf.address == 'blackhole.io'

    def test_random_address(self):
        for _ in range(25):
            addr = [str(random.randint(0, 255)) for _ in range(4)]
            cfile = create_config(('.'.join(addr),))
            Config(cfile).load()

@pytest.mark.usefixtures('reset_conf', 'cleandir')
class TestPort(unittest.TestCase):

    def test_default_port(self):
        cfile = create_config(('', ))
        conf = Config(cfile).load()
        assert conf.port == 25

    def test_str_port(self):
        cfile = create_config(('port=xcbsfbsrwgrwgsgrsgsdgrwty4y4fsg',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_port()

    def test_valid_port(self):
        cfile = create_config(('port=19',))
        conf = Config(cfile).load()
        assert conf.port == 19

    def test_lower_than_min(self):
        cfile = create_config(('port=0',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_port()

    def test_larger_than_max(self):
        cfile = create_config(('port=99999',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_port()

    @mock.patch('os.getuid', return_value=9000)
    def test_port_under_1024_no_perms(self, mock_getuid):
        cfile = create_config(('port=1023',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1

    @mock.patch('os.getuid', return_value=0)
    def test_port_under_1024_with_perms_available(self, mock_getuid):
        cfile = create_config(('port=1024',))
        conf = Config(cfile).load()
        with mock.patch('socket.socket.bind', return_value=True):
            conf.test_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1

    @mock.patch('os.getuid', return_value=0)
    @mock.patch('socket.socket.bind', side_effect=OSError(1, 'none'))
    def test_port_under_1024_with_perms_unavailable(self, mock_getuid,
                                                    mock_socket):
        cfile = create_config(('port=1023',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1
        assert mock_socket.called is True
        assert mock_socket.call_count is 1

    @mock.patch('os.getuid', return_value=9000)
    def test_port_over_1023_available(self, mock_getuid):
        cfile = create_config(('port=1024',))
        conf = Config(cfile).load()
        with mock.patch('socket.socket.bind', return_value=True):
            conf.test_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1

    @mock.patch('os.getuid', return_value=9000)
    @mock.patch('socket.socket.bind', side_effect=OSError(1, 'none'))
    def test_port_over_1023_unavailable(self, mock_getuid, mock_socket):
        cfile = create_config(('port=1024',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1
        assert mock_socket.called is True
        assert mock_socket.call_count is 1


@pytest.mark.usefixtures('reset_conf', 'cleandir')
class TestUser(unittest.TestCase):

    def test_invalid_user(self):
        cfile = create_config(('user=xcbsfbsrwgrwgsgrsgsdgrwty4y4fsg',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_user()

    def test_valid_user(self):
        cfile = create_config(('user={}'.format(getpass.getuser()),))
        conf = Config(cfile).load()
        assert conf.user == getpass.getuser()


@pytest.mark.usefixtures('reset_conf', 'cleandir')
class TestGroup(unittest.TestCase):

    def test_invalid_group(self):
        cfile = create_config(('group=xcbsfbsrwgrwgsgrsgsdgrwty4y4fsg',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_group()

    def test_valid_group(self):
        gname = grp.getgrgid(os.getgid()).gr_name
        cfile = create_config(('group={}'.format(gname)))
        conf = Config(cfile).load()
        assert conf.group == grp.getgrgid(os.getgid()).gr_name


@pytest.mark.usefixtures('reset_conf', 'cleandir')
class TestTimeout(unittest.TestCase):

    def test_default_timeout(self):
        cfile = create_config(('',))
        conf = Config(cfile).load()
        assert conf.timeout == 60

    def test_str_timeout(self):
        cfile = create_config(('timeout=xcbsfbsrwgrwgsgrsgsdgrwty4y4fsg',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_timeout()

    def test_valid_timeout(self):
        cfile = create_config(('timeout=10',))
        conf = Config(cfile).load()
        assert conf.timeout == 10


@pytest.mark.usefixtures('reset_conf', 'cleandir')
class TestTlsPort(unittest.TestCase):

    def test_default_tls_port(self):
        cfile = create_config(('',))
        conf = Config(cfile).load()
        assert conf.tls_port is None

    def test_str_tls_port(self):
        cfile = create_config(('tls_port=xcbsfbsrwgrwgsgrsgsdgrwty4y4fsg',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_port()

    def test_same_port_tls_port(self):
        cfile = create_config(('port=25', 'tls_port=25',))
        conf = Config(cfile).load()
        assert conf._port == conf._tls_port
        with pytest.raises(ConfigException):
            conf.test_tls_port()

    def test_valid_tls_port(self):
        cfile = create_config(('tls_port=19',))
        conf = Config(cfile).load()
        assert conf.tls_port == 19

    def test_tls_lower_than_min(self):
        cfile = create_config(('tls_port=0',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_port()

    def test_tls_larger_than_max(self):
        cfile = create_config(('tls_port=99999',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_port()

    @mock.patch('os.getuid', return_value=9000)
    def test_tls_under_1024_no_perms(self, mock_getuid):
        cfile = create_config(('tls_port=1023',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1

    @mock.patch('os.getuid', return_value=0)
    def test_tls_under_1024_with_perms_available(self, mock_getuid):
        cfile = create_config(('tls_port=1024',))
        conf = Config(cfile).load()
        with mock.patch('socket.socket.bind', return_value=True):
            conf.test_tls_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1

    @mock.patch('os.getuid', return_value=0)
    @mock.patch('socket.socket.bind', side_effect=OSError(1, 'none'))
    def test_tls_under_1024_with_perms_unavailable(self, mock_getuid,
                                                   mock_socket):
        cfile = create_config(('tls_port=1023',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1
        assert mock_socket.called is True
        assert mock_socket.call_count is 1

    @mock.patch('os.getuid', return_value=9000)
    def test_tls_over_1023_available(self, mock_getuid):
        cfile = create_config(('tls_port=1024',))
        conf = Config(cfile).load()
        with mock.patch('socket.socket.bind', return_value=True):
            conf.test_tls_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1

    @mock.patch('os.getuid', return_value=9000)
    @mock.patch('socket.socket.bind', side_effect=OSError(1, 'none'))
    def test_tls_over_1023_unavailable(self, mock_getuid, mock_socket):
        cfile = create_config(('tls_port=1024',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1
        assert mock_socket.called is True
        assert mock_socket.call_count is 1

@pytest.mark.usefixtures('reset_conf', 'cleandir')
class TestTls(unittest.TestCase):

    def create_file(self, name):
        cwd = os.getcwd()
        path = os.path.join(cwd, name)
        with open(path, 'w') as ffile:
            ffile.write('nothing')
        return path

    def test_disabled(self):
        cfile = create_config(('',))
        conf = Config(cfile).load()
        assert conf.test_tls_settings() is None

    def test_port_no_certkey(self):
        settings = ('tls_port=123',)
        cfile = create_config(settings)
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_settings()
        assert conf.tls_port == 123
        assert conf.tls_cert is None
        assert conf.tls_key is None

    def test_cert_no_port_key(self):
        cert = self.create_file('crt.crt')
        settings = ('tls_cert={}'.format(cert),)
        cfile = create_config(settings)
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_settings()
        assert conf.tls_port is None
        assert conf.tls_cert == cert
        assert conf.tls_key is None

    def test_key_no_port_cert(self):
        key = self.create_file('key.key')
        settings = ('tls_key={}'.format(key),)
        cfile = create_config(settings)
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_settings()
        assert conf.tls_port is None
        assert conf.tls_cert is None
        assert conf.tls_key == key

    def test_cert_key_no_port(self):
        cert = self.create_file('crt.crt')
        key = self.create_file('key.key')
        settings = ('tls_cert={}'.format(cert),
                    'tls_key={}'.format(key))
        cfile = create_config(settings)
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_settings()
        assert conf.tls_port is None
        assert conf.tls_cert == cert
        assert conf.tls_key == key

    def test_port_cert_no_key(self):
        cert = self.create_file('crt.crt')
        settings = ('tls_port=123', 'tls_cert={}'.format(cert),)
        cfile = create_config(settings)
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_settings()
        assert conf.tls_port == 123
        assert conf.tls_cert == cert
        assert conf.tls_key is None

    def test_port_key_no_cert(self):
        key = self.create_file('key.key')
        settings = ('tls_port=123', 'tls_key={}'.format(key))
        cfile = create_config(settings)
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_settings()
        assert conf.tls_port == 123
        assert conf.tls_cert is None
        assert conf.tls_key == key

    def test_port_cert_key(self):
        key = self.create_file('key.key')
        cert = self.create_file('crt.crt')
        settings = ('tls_port=123', 'tls_cert={}'.format(cert),
                    'tls_key={}'.format(key))
        cfile = create_config(settings)
        conf = Config(cfile).load()
        conf.test_tls_settings()
        assert conf.tls_port == 123
        assert conf.tls_cert == cert
        assert conf.tls_key == key


@pytest.mark.usefixtures('reset_conf', 'cleandir')
class TestDelay(unittest.TestCase):

    def test_no_delay(self):
        cfile = create_config(('',))
        conf = Config(cfile).load()
        assert conf.test_delay() is None
        assert conf.delay is None

    def test_delay_longer_than_timeout(self):
        cfile = create_config(('timeout=10', 'delay=20'))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            assert conf.test_delay()
        assert conf.delay > conf.timeout

    def test_delay(self):
        cfile = create_config(('timeout=30', 'delay=5'))
        conf = Config(cfile).load()
        assert conf.timeout > conf.delay


@pytest.mark.usefixtures('reset_conf', 'cleandir')
class TestMode(unittest.TestCase):

    def test_default(self):
        cfile = create_config(('',))
        conf = Config(cfile).load()
        assert conf.mode == 'accept'

    def test_invalid_mode(self):
        cfile = create_config(('mode=kura',))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            assert conf.test_mode()
        assert conf.mode == 'kura'

    def test_accept(self):
        cfile = create_config(('mode=accept',))
        conf = Config(cfile).load()
        assert conf.mode == 'accept'

    def test_bounce(self):
        cfile = create_config(('mode=bounce',))
        conf = Config(cfile).load()
        assert conf.mode == 'bounce'

    def test_random(self):
        cfile = create_config(('mode=random',))
        conf = Config(cfile).load()
        assert conf.mode == 'random'
