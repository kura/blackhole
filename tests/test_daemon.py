import os
from unittest import mock

import pytest

from blackhole.control.daemon import Daemon, DaemonException

from ._utils import (cleandir, reset_conf, reset_daemon, reset_supervisor,
                     create_config, create_file, Args)


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_instantiated_but_not_daemonised():
    pid = os.path.join(os.getcwd(), 'fake.pid')
    with mock.patch('os.getpid', return_value=666):
        daemon = Daemon(pid)
        assert daemon.pidfile == pid
        assert daemon.pid == 666


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_set_pid_invalid_path():
    with mock.patch('os.path.exists', return_value=False), \
        mock.patch('atexit.register'), \
            pytest.raises(DaemonException):
        Daemon('/fake/path.pid')


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_set_pid_valid_path():
    pid = os.path.join(os.getcwd(), 'fake.pid')
    with mock.patch('os.getpid', return_value=666), \
            mock.patch('atexit.register'):
        daemon = Daemon(pid)
        assert daemon.pidfile == pid
        assert daemon.pid == 666


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_get_pid_file_error():
    with mock.patch('os.path.exists', return_value=True):
        with mock.patch('builtins.open', side_effect=FileNotFoundError), \
            mock.patch('atexit.register'), \
                pytest.raises(DaemonException):
            Daemon('/fake/path.pid')
        with mock.patch('builtins.open', side_effect=IOError),\
            mock.patch('atexit.register'), \
                pytest.raises(DaemonException):
            Daemon('/fake/path.pid')
        with mock.patch('builtins.open', side_effect=PermissionError), \
            mock.patch('atexit.register'), \
                pytest.raises(DaemonException):
            Daemon('/fake/path.pid')
        with mock.patch('builtins.open', side_effect=OSError), \
            mock.patch('atexit.register'), \
                pytest.raises(DaemonException):
            Daemon('/fake/path.pid')


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_get_pid():
    pfile = create_file('test.pid', 123)
    with mock.patch('os.getpid', return_value=123), \
            mock.patch('atexit.register'):
        daemon = Daemon(pfile)
        assert daemon.pid is 123


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_delete_pid_no_exists():
    pfile = create_file('test.pid', 123)
    daemon = Daemon(pfile)
    with mock.patch('os.remove') as mock_rm, \
        mock.patch('atexit.register'), \
            mock.patch('os.path.exists', return_value=False):
        del daemon.pid
    assert mock_rm.called is False


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_delete_pid():
    pfile = create_file('test.pid', 123)
    with mock.patch('os.getpid', return_value=123), \
            mock.patch('atexit.register'):
        daemon = Daemon(pfile)
        assert daemon.pid is 123
        del daemon.pid
        assert daemon.pid is None


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_delete_pid_exit():
    pfile = create_file('test.pid', 123)
    with mock.patch('os.getpid', return_value=123), \
            mock.patch('atexit.register'):
        daemon = Daemon(pfile)
        assert daemon.pid is 123
        daemon._exit()
        assert daemon.pid is None


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_fork():
    pfile = create_file('test.pid', 123)
    with mock.patch('atexit.register'):
        daemon = Daemon(pfile)
    with mock.patch('os.fork', return_value=9999) as mock_fork, \
            mock.patch('os._exit') as mock_exit:
        daemon.fork()
    assert mock_fork.called is True
    assert mock_exit.called is True


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_fork_error():
    pfile = create_file('test.pid', 123)
    with mock.patch('atexit.register'):
        daemon = Daemon(pfile)
    with mock.patch('os.fork', side_effect=OSError) as mock_fork, \
            pytest.raises(DaemonException):
        daemon.fork()
    assert mock_fork.called is True


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_daemonise():
    pfile = create_file('test.pid', 123)
    with mock.patch('blackhole.control.daemon.Daemon.'
                    'fork') as mock_fork, \
        mock.patch('os.chdir') as mock_chdir, \
        mock.patch('os.setsid') as mock_setsid, \
        mock.patch('os.umask') as mock_umask, \
        mock.patch('atexit.register') as mock_atexit, \
            mock.patch('os.getpid', return_value=123):
        daemon = Daemon(pfile)
        daemon.daemonize()
    assert mock_fork.called is True
    assert mock_chdir.called is True
    assert mock_setsid.called is True
    assert mock_umask.called is True
    assert mock_atexit.called is True
