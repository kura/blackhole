import os
import tempfile
from unittest import mock

import pytest

from blackhole.application import run
from blackhole.config import Config, Singleton as CSingleton
from blackhole.daemon import Singleton as DSingleton
from blackhole.exceptions import (ConfigException, DaemonException,
                                  BlackholeRuntimeException)
from blackhole.supervisor import Singleton as SSingleton


@pytest.fixture()
def cleandir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)


@pytest.fixture()
def reset_conf():
    CSingleton._instances = {}


@pytest.fixture()
def reset_daemon():
    DSingleton._instances = {}


@pytest.fixture()
def reset_supervisor():
    SSingleton._instances = {}


def create_config(data):
    cwd = os.getcwd()
    path = os.path.join(cwd, 'test.conf')
    with open(path, 'w') as cfile:
        cfile.write('\n'.join(data))
    return path


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_run_test():
    cfile = create_config(('', ))
    with mock.patch('sys.argv', ['blackhole', '-t', '-c', cfile]), \
        mock.patch('blackhole.config.Config.test_port', return_value=True), \
            pytest.raises(SystemExit) as err:
        run()
    assert str(err.value) == '0'


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_run_test_fails():
    cfile = create_config(('listen=127.0.0.1:0', ))
    with mock.patch('sys.argv', ['blackhole', '-t', '-c', cfile]), \
            pytest.raises(SystemExit) as err:
        run()
    assert str(err.value) == '64'


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_run_load_test_fails():
    cfile = create_config(('listen=127.0.0.1:0', ))
    with mock.patch('sys.argv', ['blackhole', '-t', '-c', cfile]), \
        mock.patch('blackhole.config.Config.test',
                   side_effect=ConfigException()), \
            pytest.raises(SystemExit) as err:
        run()
    assert str(err.value) == '64'


@pytest.mark.usefixtures('reset_supervisor', 'reset_daemon', 'reset_conf',
                         'cleandir')
def test_run_foreground():
    pidfile = os.path.join(os.getcwd(), 'blackhole-test.pid')
    cfile = create_config(('listen=127.0.0.1:9000',
                           'pidfile={}'.format(pidfile)))
    Config(cfile).load()

    with mock.patch('sys.argv', ['-c {}'.format(cfile)]), \
        mock.patch('blackhole.config.Config.test'), \
        mock.patch('blackhole.config.warn_options'), \
        mock.patch('atexit.register'), \
        mock.patch('os.chown'), \
        mock.patch('blackhole.supervisor.Supervisor.generate_servers'), \
        mock.patch('blackhole.control.pid_permissions'), \
        mock.patch('blackhole.control.setgid'), \
        mock.patch('blackhole.control.setuid'), \
        mock.patch('blackhole.supervisor.Supervisor.run'), \
            pytest.raises(SystemExit) as err:
        run()
    assert str(err.value) == '0'


@pytest.mark.usefixtures('reset_supervisor', 'reset_daemon', 'reset_conf',
                         'cleandir')
def test_run_foreground_pid_error():
    pidfile = os.path.join(os.getcwd(), 'blackhole-test.pid')
    cfile = create_config(('listen=127.0.0.1:9000',
                           'pidfile={}'.format(pidfile)))
    Config(cfile).load()

    with mock.patch('sys.argv', ['-c {}'.format(cfile)]), \
        mock.patch('blackhole.config.Config.test'), \
        mock.patch('blackhole.config.warn_options'), \
        mock.patch('os.getpid', return_value=1234), \
        mock.patch('atexit.register', side_effect=DaemonException), \
            pytest.raises(SystemExit) as err:
        run()
    assert str(err.value) == '64'


@pytest.mark.usefixtures('reset_supervisor', 'reset_daemon', 'reset_conf',
                         'cleandir')
def test_run_foreground_socket_error():
    pidfile = os.path.join(os.getcwd(), 'blackhole-test.pid')
    cfile = create_config(('listen=127.0.0.1:9000',
                           'pidfile={}'.format(pidfile)))
    Config(cfile).load()

    with mock.patch('sys.argv', ['-c {}'.format(cfile)]), \
        mock.patch('blackhole.config.Config.test'), \
        mock.patch('blackhole.config.warn_options'), \
        mock.patch('atexit.register'), \
        mock.patch('blackhole.supervisor.Supervisor.close_socks'), \
        mock.patch('blackhole.supervisor.Supervisor.generate_servers',
                   side_effect=BlackholeRuntimeException), \
            pytest.raises(SystemExit) as err:
        run()
    assert str(err.value) == '77'


@pytest.mark.usefixtures('reset_supervisor', 'reset_daemon', 'reset_conf',
                         'cleandir')
def test_run_background():
    pidfile = os.path.join(os.getcwd(), 'blackhole-test.pid')
    cfile = create_config(('listen=127.0.0.1:9000',
                           'pidfile={}'.format(pidfile)))
    Config(cfile).load()

    with mock.patch('sys.argv', ['-c {}'.format(cfile), '-b']), \
        mock.patch('blackhole.config.Config.test'), \
        mock.patch('blackhole.config.warn_options'), \
        mock.patch('atexit.register'), \
        mock.patch('os.chown'), \
        mock.patch('blackhole.supervisor.Supervisor.generate_servers'), \
        mock.patch('blackhole.daemon.Daemon.daemonize'), \
        mock.patch('blackhole.control.pid_permissions'), \
        mock.patch('blackhole.control.setgid'), \
        mock.patch('blackhole.control.setuid'), \
        mock.patch('blackhole.supervisor.Supervisor.run'), \
            pytest.raises(SystemExit) as err:
        run()
    assert str(err.value) == '0'


@pytest.mark.usefixtures('reset_supervisor', 'reset_daemon', 'reset_conf',
                         'cleandir')
def test_run_daemon_daemonize_error():
    pidfile = os.path.join(os.getcwd(), 'blackhole-test.pid')
    cfile = create_config(('listen=127.0.0.1:9000',
                           'pidfile={}'.format(pidfile)))
    Config(cfile).load()

    with mock.patch('sys.argv', ['-c {}'.format(cfile), '-b']), \
        mock.patch('blackhole.config.Config.test'), \
        mock.patch('blackhole.config.warn_options'), \
        mock.patch('atexit.register'), \
        mock.patch('os.chown'), \
        mock.patch('blackhole.supervisor.Supervisor.generate_servers'), \
        mock.patch('os.fork', side_effect=OSError), \
        mock.patch('blackhole.supervisor.Supervisor.'
                   'close_socks') as mock_close, \
            pytest.raises(SystemExit) as err:
        run()
    assert str(err.value) == '77'
    assert mock_close.called is True
