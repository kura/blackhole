import os
import tempfile
from unittest import mock

import pytest

from blackhole.config import Singleton as CSingleton
from blackhole.daemon import Daemon, Singleton as DSingleton, DaemonException


@pytest.fixture()
def cleandir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)


def create_file(name, data='nothing'):
    cwd = os.getcwd()
    path = os.path.join(cwd, name)
    with open(path, 'w') as ffile:
        ffile.write('{}\n'.format(str(data)))
    return path


@pytest.fixture()
def reset():
    CSingleton._instances = {}
    DSingleton._instances = {}


@pytest.mark.usefixtures('reset', 'cleandir')
def test_instantiated_but_not_daemonised():
    pid = os.path.join(os.getcwd(), 'fake.pid')
    with mock.patch('os.getpid', return_value=666):
        daemon = Daemon(pid)
        assert daemon.pidfile == pid
        assert daemon.pid == 666


@pytest.mark.usefixtures('reset')
def test_set_pid_invalid_path():
    with mock.patch('os.path.exists', return_value=False), \
            pytest.raises(DaemonException):
        Daemon('/fake/path.pid')


@pytest.mark.usefixtures('reset', 'cleandir')
def test_set_pid_valid_path():
    pid = os.path.join(os.getcwd(), 'fake.pid')
    with mock.patch('os.getpid', return_value=666):
        daemon = Daemon(pid)
        assert daemon.pidfile == pid
        assert daemon.pid == 666


@pytest.mark.usefixtures('reset')
@mock.patch('os.path.exists', return_value=True)
def test_get_pid_file_error(_):
    with mock.patch('builtins.open', side_effect=FileNotFoundError):
        with pytest.raises(DaemonException):
            Daemon('/fake/path.pid')
    with mock.patch('builtins.open', side_effect=IOError):
        with pytest.raises(DaemonException):
            Daemon('/fake/path.pid')
    with mock.patch('builtins.open', side_effect=PermissionError):
        with pytest.raises(DaemonException):
            Daemon('/fake/path.pid')
    with mock.patch('builtins.open', side_effect=OSError):
        with pytest.raises(DaemonException):
            Daemon('/fake/path.pid')


@pytest.mark.usefixtures('reset', 'cleandir')
def test_get_pid():
    pfile = create_file('test.pid', 123)
    with mock.patch('os.getpid', return_value=123):
        daemon = Daemon(pfile)
        assert daemon.pid is 123


@pytest.mark.usefixtures('reset', 'cleandir')
def test_delete_pid_no_exists():
    pfile = create_file('test.pid', 123)
    daemon = Daemon(pfile)
    with mock.patch('os.remove') as mock_rm, \
            mock.patch('os.path.exists', return_value=False):
        del daemon.pid
    assert mock_rm.called is False


@pytest.mark.usefixtures('reset', 'cleandir')
def test_delete_pid():
    pfile = create_file('test.pid', 123)
    with mock.patch('os.getpid', return_value=123):
        daemon = Daemon(pfile)
        assert daemon.pid is 123
        del daemon.pid
        assert daemon.pid is None


@pytest.mark.usefixtures('reset', 'cleandir')
def test_delete_pid_exit():
    pfile = create_file('test.pid', 123)
    with mock.patch('os.getpid', return_value=123):
        daemon = Daemon(pfile)
        assert daemon.pid is 123
        daemon.exit()
        assert daemon.pid is None


@pytest.mark.usefixtures('reset', 'cleandir')
def test_fork():
    pfile = create_file('test.pid', 123)
    daemon = Daemon(pfile)
    with mock.patch('os.fork', return_value=9999) as mock_fork, \
            mock.patch('os._exit') as mock_exit:
        daemon.fork()
    assert mock_fork.called is True
    assert mock_exit.called is True


@pytest.mark.usefixtures('reset', 'cleandir')
@mock.patch('os.fork', side_effect=OSError)
def test_fork_error(mock_fork):
    pfile = create_file('test.pid', 123)
    daemon = Daemon(pfile)
    with pytest.raises(DaemonException):
        daemon.fork()
    assert mock_fork.called is True


@pytest.mark.usefixtures('reset', 'cleandir')
@mock.patch('blackhole.daemon.Daemon.fork')
@mock.patch('os.chdir')
@mock.patch('os.setsid')
@mock.patch('os.umask')
@mock.patch('atexit.register')
@mock.patch('os.getpid', return_value=123)
def test_daemonise(mock_fork, mock_chdir, mock_setsid, mock_umask, mock_atexit,
                   mock_getpid):
    pfile = create_file('test.pid', 123)
    daemon = Daemon(pfile)
    daemon.daemonize()
    assert mock_fork.called is True
    assert mock_chdir.called is True
    assert mock_setsid.called is True
    assert mock_umask.called is True
    assert mock_atexit.called is True
