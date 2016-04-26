import asyncio
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

import blackhole
from blackhole.config import Singleton, Config
from blackhole.control import (create_server, start_servers, stop_servers,
                               setuid, setgid, tls_context, create_socket)


logging.getLogger('blackhole').addHandler(logging.NullHandler())


@pytest.fixture()
def cleandir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)


@pytest.fixture()
def reset_conf():
    Singleton._instances = {}


@pytest.fixture()
def reset_servers():
    del blackhole.control._servers
    blackhole.control._servers = []


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
    ctx = tls_context()
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
        tls_context(use_tls=True)


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
        tls_context(use_tls=True)


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
    with mock.patch('ssl.SSLContext.load_cert_chain'):
        with mock.patch('ssl.SSLContext.load_dh_params') as dh:
            tls_context(use_tls=True)
    assert dh.called is True


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
def test_create_ipv6_socket_fails():
    with mock.patch('socket.socket.bind', side_effect=OSError):
        with pytest.raises(SystemExit) as err:
            create_socket('::', 25, socket.AF_INET)
    assert str(err.value) == '77'


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
def test_create_ipv6_socket_without_reuseport():
    SO_REUSEPORT = True
    if hasattr(socket, 'SO_REUSEPORT'):
        orig = socket.SO_REUSEPORT
        del socket.SO_REUSEPORT
        SO_REUSEPORT = False
    with mock.patch('socket.socket.bind'):
        create_socket('::', 25, socket.AF_INET)
    if SO_REUSEPORT is False:
        socket.SO_REUSEPORT = orig


def test_create_ipv4_socket_fails():
    with mock.patch('socket.socket.bind', side_effect=OSError):
        with pytest.raises(SystemExit) as err:
            create_socket('127.0.0.1', 25, socket.AF_INET)
    assert str(err.value) == '77'


def test_create_ipv4_socket_without_reuseport():
    SO_REUSEPORT = True
    if hasattr(socket, 'SO_REUSEPORT'):
        orig = socket.SO_REUSEPORT
        del socket.SO_REUSEPORT
        SO_REUSEPORT = False
    with mock.patch('socket.socket.bind'):
        create_socket('127.0.0.1', 25, socket.AF_INET)
    if SO_REUSEPORT is False:
        socket.SO_REUSEPORT = orig


@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind', side_effect=OSError)
def test_create_server_ipv4_bind_fails(mock_sock):
    assert len(blackhole.control._servers) is 0
    cfile = create_config(('listen=127.0.0.1:9000',))
    Config(cfile).load()
    with pytest.raises(SystemExit) as err:
        create_server('127.0.0.1', 9000, socket.AF_INET)
    assert str(err.value) == '77'
    assert len(blackhole.control._servers) is 0
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind', side_effect=OSError)
def test_create_server_ipv6_bind_fails(mock_sock):
    assert len(blackhole.control._servers) is 0
    cfile = create_config(('listen=:::9000',))
    Config(cfile).load()
    with pytest.raises(SystemExit) as err:
        create_server('::', 9000, socket.AF_INET)
    assert str(err.value) == '77'
    assert len(blackhole.control._servers) is 0
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
def test_create_server_ipv4_bind_works(mock_sock):
    assert len(blackhole.control._servers) is 0
    cfile = create_config(('listen=127.0.0.1:9000',))
    Config(cfile).load()
    create_server('127.0.0.1', 9000, socket.AF_INET)
    assert len(blackhole.control._servers) is 1
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
def test_create_server_ipv6_bind_works(mock_sock):
    assert len(blackhole.control._servers) is 0
    cfile = create_config(('listen=:::9000',))
    Config(cfile).load()
    create_server('::', 9000, socket.AF_INET)
    assert len(blackhole.control._servers) is 1
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind', side_effect=OSError)
def test_create_server_ipv4_tls_bind_fails(mock_sock):
    assert len(blackhole.control._servers) is 0
    cfile = create_config(('tls_listen=127.0.0.1:9000',))
    Config(cfile).load()
    with pytest.raises(SystemExit) as err:
        create_server('127.0.0.1', 9000, socket.AF_INET)
    assert str(err.value) == '77'
    assert len(blackhole.control._servers) is 0
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind', side_effect=OSError)
def test_create_server_ipv6_tls_bind_fails(mock_sock):
    assert len(blackhole.control._servers) is 0
    cfile = create_config(('tls_listen=:::9000',))
    Config(cfile).load()
    with pytest.raises(SystemExit) as err:
        create_server('::', 9000, socket.AF_INET)
    assert str(err.value) == '77'
    assert len(blackhole.control._servers) is 0
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
@mock.patch('ssl.create_default_context')
def test_create_server_tls_ipv4_bind_works(mock_sock, mock_ssl):
    assert len(blackhole.control._servers) is 0
    cfile = create_config(('listen=127.0.0.1:25',
                           'tls_listen=127.0.0.1:9000',))
    conf = Config(cfile).load()
    conf.args = Args()
    conf.args.less_secure = False
    create_server('127.0.0.1', 9000, socket.AF_INET, use_tls=True)
    assert len(blackhole.control._servers) is 1
    assert mock_sock.called is True
    assert mock_sock.call_count is 1
    assert mock_ssl.called is True
    assert mock_ssl.call_count is 1


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
@mock.patch('ssl.create_default_context')
def test_create_server_tls_ipv6_bind_works(mock_sock, mock_ssl):
    assert len(blackhole.control._servers) is 0
    cfile = create_config(('listen=:::25',
                           'tls_listen=:::9000',))
    conf = Config(cfile).load()
    conf.args = Args()
    conf.args.less_secure = False
    create_server('::', 9000, socket.AF_INET, use_tls=True)
    assert len(blackhole.control._servers) is 1
    assert mock_sock.called is True
    assert mock_sock.call_count is 1
    assert mock_ssl.called is True
    assert mock_ssl.call_count is 1


@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
def test_ipv4_start_servers(mock_bind):
    cfile = create_config(('listen=127.0.0.1:9000',))
    Config(cfile).load()
    start_servers()
    assert len(blackhole.control._servers) is 1
    assert mock_bind.called is True
    assert mock_bind.call_count is 1


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
@mock.patch('ssl.create_default_context')
def test_ipv4_start_servers_tls(_, __):
    tls_cert = create_file('cert.cert')
    tls_key = create_file('key.key')
    cfile = create_config(('listen=127.0.0.1:25', 'tls_listen=127.0.0.1:9000',
                           'tls_cert={}'.format(tls_cert),
                           'tls_key={}'.format(tls_key)))
    conf = Config(cfile).load()
    conf.args = Args()
    conf.args.less_secure = False
    start_servers()
    assert len(blackhole.control._servers) is 2


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
def test_ipv6_start_servers(mock_bind):
    cfile = create_config(('listen=:::9000',))
    Config(cfile).load()
    start_servers()
    assert len(blackhole.control._servers) is 1
    assert mock_bind.called is True
    assert mock_bind.call_count is 1


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
@mock.patch('ssl.create_default_context')
def test_ipv6_start_servers_tls(_, __):
    tls_cert = create_file('cert.cert')
    tls_key = create_file('key.key')
    cfile = create_config(('listen=:::25', 'tls_listen=:::9000',
                           'tls_cert={}'.format(tls_cert),
                           'tls_key={}'.format(tls_key)))
    conf = Config(cfile).load()
    conf.args = Args()
    conf.args.less_secure = False
    start_servers()
    assert len(blackhole.control._servers) is 2


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
def test_ipv4_and_ipv6_start_servers(mock_bind):
    cfile = create_config(('listen=127.0.0.1:9000,:::9000',))
    Config(cfile).load()
    start_servers()
    assert len(blackhole.control._servers) is 2
    assert mock_bind.called is True
    assert mock_bind.call_count is 2


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
@mock.patch('ssl.create_default_context')
def test_ipv4_and_ipv6_start_servers_tls(_, __):
    tls_cert = create_file('cert.cert')
    tls_key = create_file('key.key')
    cfile = create_config(('listen=127.0.0.1:25,:::25',
                           'tls_listen=127.0.0.1:9000,:::9000',
                           'tls_cert={}'.format(tls_cert),
                           'tls_key={}'.format(tls_key)))
    conf = Config(cfile).load()
    conf.args = Args()
    conf.args.less_secure = False
    start_servers()
    assert len(blackhole.control._servers) is 4


@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('asyncio.base_events.Server')
@mock.patch('asyncio.get_event_loop')
def test_stop_servers(mock_server, mock_loop):
    blackhole.control._servers = [asyncio.base_events.Server([], []),
                                  asyncio.base_events.Server([], []),
                                  asyncio.base_events.Server([], [])]
    with mock.patch('os.path.exists', return_value=False):
        stop_servers()
    assert len(blackhole.control._servers) is 0


class Grp(mock.MagicMock):
    gr_name = 'testgroup'
    gr_gid = 9000


@pytest.mark.usefixtures('reset_conf', 'cleandir')
@mock.patch('grp.getgrnam')
@mock.patch('os.setgid')
def test_setgid(mock_getgrnam, mock_setgid):
    cfile = create_config(('group=abc',))
    Config(cfile).load()
    setgid()
    assert mock_getgrnam.called is True
    assert mock_setgid.called is True


@pytest.mark.usefixtures('reset_conf', 'cleandir')
@mock.patch('grp.getgrgid', return_value=Grp())
def test_setgid_same_group(mock_getgrnam):
    cfile = create_config(('group=testgroup',))
    Config(cfile).load()
    assert setgid() is None
    assert mock_getgrnam.called is True


@pytest.mark.usefixtures('reset_conf', 'cleandir')
@mock.patch('grp.getgrnam', side_effect=KeyError)
def test_setgid_invalid_group(_):
    cfile = create_config(('group=testgroup',))
    Config(cfile).load()
    with pytest.raises(SystemExit) as err:
        setgid()
    assert str(err.value) == '64'


@pytest.mark.usefixtures('reset_conf', 'cleandir')
@mock.patch('grp.getgrnam', side_effect=PermissionError)
def test_setgid_no_perms(_):
    cfile = create_config(('group=testgroup',))
    Config(cfile).load()
    with pytest.raises(SystemExit) as err:
        setgid()
    assert str(err.value) == '77'


class Pwd(mock.MagicMock):
    pwd_uid = 9000


@pytest.mark.usefixtures('reset_conf', 'cleandir')
@mock.patch('pwd.getpwnam')
@mock.patch('os.setuid')
def test_setuid(mock_getpwnam, mock_setuid):
    cfile = create_config(('user=abc',))
    Config(cfile).load()
    setuid()
    assert mock_getpwnam.called is True
    assert mock_setuid.called is True


@pytest.mark.usefixtures('reset_conf', 'cleandir')
@mock.patch('getpass.getuser', return_value='testuser')
def test_setuid_same_user(mock_getuser):
    cfile = create_config(('user=testuser',))
    Config(cfile).load()
    assert setuid() is None
    assert mock_getuser.called is True


@pytest.mark.usefixtures('reset_conf', 'cleandir')
@mock.patch('pwd.getpwnam', side_effect=KeyError)
def test_setuid_invalid_user(_):
    cfile = create_config(('user=testuser',))
    Config(cfile).load()
    with pytest.raises(SystemExit) as err:
        setuid()
    assert str(err.value) == '64'


@pytest.mark.usefixtures('reset_conf', 'cleandir')
@mock.patch('pwd.getpwnam', side_effect=PermissionError)
def test_setuid_no_perms(_):
    cfile = create_config(('user=testuser',))
    Config(cfile).load()
    with pytest.raises(SystemExit) as err:
        setuid()
    assert str(err.value) == '77'
