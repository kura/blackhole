import asyncio
import logging
import os
import tempfile
from unittest import mock

import pytest

import blackhole
from blackhole.config import Singleton, Config
from blackhole.control import (create_server, start_servers, stop_servers,
                               setuid, setgid)


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


@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind', side_effect=OSError)
def test_create_server_bind_fails(mock_sock):
    assert len(blackhole.control._servers) is 0
    cfile = create_config(('port=9000',))
    Config(cfile).load()
    with pytest.raises(SystemExit) as err:
        create_server()
    assert str(err.value) == '77'
    assert len(blackhole.control._servers) is 0
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
def test_create_server_bind_works(mock_sock):
    assert len(blackhole.control._servers) is 0
    cfile = create_config(('port=9000',))
    Config(cfile).load()
    create_server()
    assert len(blackhole.control._servers) is 1
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind', side_effect=OSError)
def test_create_server_tls_bind_fails(mock_sock):
    assert len(blackhole.control._servers) is 0
    cfile = create_config(('tls_port=9000',))
    Config(cfile).load()
    with pytest.raises(SystemExit) as err:
        create_server()
    assert str(err.value) == '77'
    assert len(blackhole.control._servers) is 0
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
@mock.patch('ssl.create_default_context')
def test_create_server_tls_bind_works(mock_sock, mock_ssl):
    assert len(blackhole.control._servers) is 0
    cfile = create_config(('port=25', 'tls_port=9000',))
    Config(cfile).load()
    create_server(use_tls=True)
    assert len(blackhole.control._servers) is 1
    assert mock_sock.called is True
    assert mock_sock.call_count is 1
    assert mock_ssl.called is True
    assert mock_ssl.call_count is 1


@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
def test_start_servers(mock_bind):
    cfile = create_config(('port=9000',))
    Config(cfile).load()
    start_servers()
    assert len(blackhole.control._servers) is 1
    assert mock_bind.called is True
    assert mock_bind.call_count is 1


@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('socket.socket.bind')
@mock.patch('ssl.create_default_context')
def test_start_servers_tls(_, __):
    tls_cert = create_file('cert.cert')
    tls_key = create_file('key.key')
    cfile = create_config(('port=25', 'tls_port=9000',
                           'tls_cert={}'.format(tls_cert),
                           'tls_key={}'.format(tls_key)))
    Config(cfile).load()
    start_servers()
    assert len(blackhole.control._servers) is 2


@pytest.mark.usefixtures('reset_servers', 'reset_conf', 'cleandir')
@mock.patch('asyncio.base_events.Server')
@mock.patch('asyncio.get_event_loop')
def test_stop_servers(mock_server, mock_loop):
    blackhole.control._servers = [asyncio.base_events.Server([], []),
                                  asyncio.base_events.Server([], []),
                                  asyncio.base_events.Server([], [])]
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
