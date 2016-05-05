import logging
import os
try:
    import ssl
except ImportError:
    ssl = None
import socket
import tempfile
import unittest
from unittest import mock

import pytest

from blackhole.config import Singleton, Config
from blackhole.control import (_context, _socket, _server, setuid, setgid,
                               pid_permissions)


logging.getLogger('blackhole').addHandler(logging.NullHandler())


@pytest.fixture()
def cleandir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)


@pytest.fixture()
def reset_conf():
    Singleton._instances = {}


@pytest.mark.usefixtures('reset_conf')
def create_config(data):
    cwd = os.getcwd()
    path = os.path.join(cwd, 'test.conf')
    with open(path, 'w') as cfile:
        cfile.write('\n'.join(data))
    return path


def create_file(name):
    cwd = os.getcwd()
    path = os.path.join(cwd, name)
    with open(path, 'w') as ffile:
        ffile.write('nothing')
    return path


def test_tls_context_no_config():
    ctx = _context()
    assert ctx is None


class Args(object):
    pass


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_tls_context_no_dhparams():
    tls_cert = create_file('cert.cert')
    tls_key = create_file('key.key')
    cfile = create_config(('listen=127.0.0.1:25', 'tls_listen=127.0.0.1:9000',
                           'tls_cert={}'.format(tls_cert),
                           'tls_key={}'.format(tls_key),))
    conf = Config(cfile).load()
    conf.args = Args()
    conf.args.less_secure = False
    with mock.patch('ssl.SSLContext.load_cert_chain'):
        _context(use_tls=True)


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_tls_context_less_secure():
    tls_cert = create_file('cert.cert')
    tls_key = create_file('key.key')
    cfile = create_config(('listen=127.0.0.1:25', 'tls_listen=127.0.0.1:9000',
                           'tls_cert={}'.format(tls_cert),
                           'tls_key={}'.format(tls_key),))
    conf = Config(cfile).load()
    conf.args = Args()
    conf.args.less_secure = True
    with mock.patch('ssl.SSLContext.load_cert_chain'):
        _context(use_tls=True)


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_tls_context_dhparams():
    tls_cert = create_file('cert.cert')
    tls_key = create_file('key.key')
    tls_dhparams = create_file('dhparams.pem')
    cfile = create_config(('listen=127.0.0.1:25', 'tls_listen=127.0.0.1:9000',
                           'tls_cert={}'.format(tls_cert),
                           'tls_key={}'.format(tls_key),
                           'tls_dhparams={}'.format(tls_dhparams)))
    conf = Config(cfile).load()
    conf.args = Args()
    conf.args.less_secure = False
    with mock.patch('ssl.SSLContext.load_cert_chain'), \
            mock.patch('ssl.SSLContext.load_dh_params') as dh:
        _context(use_tls=True)
    assert dh.called is True


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
def test_create_ipv6_socket_fails():
    with mock.patch('socket.socket.bind', side_effect=OSError), \
            pytest.raises(SystemExit) as err:
        _socket('::', 25, socket.AF_INET)
    assert str(err.value) == '77'


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
def test_create_ipv6_socket_without_reuseport():
    SO_REUSEPORT = True
    if hasattr(socket, 'SO_REUSEPORT'):
        orig = socket.SO_REUSEPORT
        del socket.SO_REUSEPORT
        SO_REUSEPORT = False
    with mock.patch('socket.socket.bind'):
        _socket('::', 25, socket.AF_INET)
    if SO_REUSEPORT is False:
        socket.SO_REUSEPORT = orig


def test_create_ipv4_socket_fails():
    with mock.patch('socket.socket.bind', side_effect=OSError), \
            pytest.raises(SystemExit) as err:
        _socket('127.0.0.1', 25, socket.AF_INET)
    assert str(err.value) == '77'


def test_create_ipv4_socket_without_reuseport():
    SO_REUSEPORT = True
    if hasattr(socket, 'SO_REUSEPORT'):
        orig = socket.SO_REUSEPORT
        del socket.SO_REUSEPORT
        SO_REUSEPORT = False
    with mock.patch('socket.socket.bind'):
        _socket('127.0.0.1', 25, socket.AF_INET)
    if SO_REUSEPORT is False:
        socket.SO_REUSEPORT = orig


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_create_server_ipv4_bind_fails():
    cfile = create_config(('listen=127.0.0.1:9000',))
    Config(cfile).load()
    with mock.patch('socket.socket.bind', side_effect=OSError) as mock_sock, \
            pytest.raises(SystemExit) as err:
        _server('127.0.0.1', 9000, socket.AF_INET)
    assert str(err.value) == '77'
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_create_server_ipv6_bind_fails():
    cfile = create_config(('listen=:::9000',))
    Config(cfile).load()
    with mock.patch('socket.socket.bind', side_effect=OSError) as mock_sock, \
            pytest.raises(SystemExit) as err:
        _server('::', 9000, socket.AF_INET6)
    assert str(err.value) == '77'
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@pytest.mark.usefixtures('reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
def test_create_server_ipv4_bind_works(mock_sock):
    cfile = create_config(('listen=127.0.0.1:9000',))
    Config(cfile).load()
    _server('127.0.0.1', 9000, socket.AF_INET)
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_create_server_ipv6_bind_works():
    cfile = create_config(('listen=:::9000',))
    Config(cfile).load()
    with mock.patch('socket.socket.bind') as mock_sock:
        _server('::', 9000, socket.AF_INET6)
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_create_server_ipv4_tls_bind_fails():
    cfile = create_config(('tls_listen=127.0.0.1:9000',))
    Config(cfile).load()
    with mock.patch('socket.socket.bind', side_effect=OSError) as mock_sock, \
            pytest.raises(SystemExit) as err:
        _server('127.0.0.1', 9000, socket.AF_INET)
    assert str(err.value) == '77'
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_create_server_ipv6_tls_bind_fails():
    cfile = create_config(('tls_listen=:::9000',))
    Config(cfile).load()
    with mock.patch('socket.socket.bind', side_effect=OSError) as mock_sock, \
            pytest.raises(SystemExit) as err:
        _server('::', 9000, socket.AF_INET6)
    assert str(err.value) == '77'
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_create_server_tls_ipv4_bind_works():
    cfile = create_config(('listen=127.0.0.1:25',
                           'tls_listen=127.0.0.1:9000',))
    conf = Config(cfile).load()
    conf.args = Args()
    conf.args.less_secure = False
    with mock.patch('socket.socket.bind') as mock_sock, \
            mock.patch('ssl.create_default_context') as mock_ssl:
        _server('127.0.0.1', 9000, socket.AF_INET, use_tls=True)
    assert mock_sock.called is True
    assert mock_sock.call_count is 1
    assert mock_ssl.called is True
    assert mock_ssl.call_count is 1


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_create_server_tls_ipv6_bind_works():
    cfile = create_config(('listen=:::25',
                           'tls_listen=:::9000',))
    conf = Config(cfile).load()
    conf.args = Args()
    conf.args.less_secure = False
    with mock.patch('socket.socket.bind') as mock_sock, \
            mock.patch('ssl.create_default_context') as mock_ssl:
        _server('::', 9000, socket.AF_INET6, use_tls=True)
    assert mock_sock.called is True
    assert mock_sock.call_count is 1
    assert mock_ssl.called is True
    assert mock_ssl.call_count is 1


class Grp(mock.MagicMock):
    gr_name = 'testgroup'
    gr_gid = 9000


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_setgid():
    cfile = create_config(('group=abc',))
    with mock.patch('grp.getgrnam') as mock_getgrnam, \
            mock.patch('os.setgid') as mock_setgid:
        Config(cfile).load()
        setgid()
    assert mock_getgrnam.called is True
    assert mock_setgid.called is True


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_setgid_same_group():
    cfile = create_config(('group=testgroup',))
    with mock.patch('grp.getgrgid', return_value=Grp()) as mock_getgrnam:
        Config(cfile).load()
        assert setgid() is None
    assert mock_getgrnam.called is True


@pytest.mark.usefixtures('reset_conf', 'cleandir')
@mock.patch('grp.getgrnam', side_effect=KeyError)
def test_setgid_invalid_group(_):
    cfile = create_config(('group=testgroup',))
    with pytest.raises(SystemExit) as err:
        Config(cfile).load()
        setgid()
    assert str(err.value) == '64'


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_setgid_no_perms():
    cfile = create_config(('group=testgroup',))
    with mock.patch('grp.getgrnam', side_effect=PermissionError), \
            pytest.raises(SystemExit) as err:
        Config(cfile).load()
        setgid()
    assert str(err.value) == '77'


class Pwd(mock.MagicMock):
    pwd_uid = 9000


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_setuid():
    cfile = create_config(('user=abc',))
    with mock.patch('pwd.getpwnam') as mock_getpwnam, \
            mock.patch('os.setuid') as mock_setuid:
        Config(cfile).load()
        setuid()
    assert mock_getpwnam.called is True
    assert mock_setuid.called is True


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_setuid_same_user():
    cfile = create_config(('user=testuser',))
    with mock.patch('getpass.getuser',
                    return_value='testuser') as mock_getuser:
                    Config(cfile).load()
                    assert setuid() is None
    assert mock_getuser.called is True


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_setuid_invalid_user():
    cfile = create_config(('user=testuser',))
    with mock.patch('pwd.getpwnam', side_effect=KeyError), \
            pytest.raises(SystemExit) as err:
        Config(cfile).load()
        setuid()
    assert str(err.value) == '64'


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_setuid_no_perms():
    cfile = create_config(('user=testuser',))
    with mock.patch('pwd.getpwnam', side_effect=PermissionError), \
            pytest.raises(SystemExit) as err:
        Config(cfile).load()
        setuid()
    assert str(err.value) == '77'


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_set_pid_permissions():
    pidfile = os.path.join(os.getcwd(), 'pid.pid')
    cfile = create_config(('user=testuser', 'group=testgroup',
                           'pidfile={}'.format(pidfile)))
    Config(cfile).load()
    with mock.patch('pwd.getpwnam', side_effect=KeyError), \
            pytest.raises(SystemExit) as err:
        pid_permissions()
    assert str(err.value) == '64'
    with mock.patch('grp.getgrgid', side_effect=KeyError), \
            pytest.raises(SystemExit) as err:
        pid_permissions()
    assert str(err.value) == '64'
    with mock.patch('os.chown', side_effect=PermissionError), \
            pytest.raises(SystemExit) as err:
        pid_permissions()
    assert str(err.value) == '64'
