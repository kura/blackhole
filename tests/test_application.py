import os
import tempfile
from unittest import mock

import pytest

from blackhole.application import run
from blackhole.config import Config, Singleton as CSingleton
from blackhole.daemon import Singleton as DSingleton
from blackhole.exceptions import ConfigException, DaemonException


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


@pytest.mark.usefixtures('reset_conf')
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


class Args(object):
    pass


@pytest.mark.usefixtures('reset_daemon', 'reset_conf', 'cleandir')
def test_run_foreground():
    cfile = create_config(('listen=127.0.0.1:9000',))
    Config(cfile).load()
    args = Args()

    with mock.patch('sys.argv', ['-c {}'.format(cfile)]), \
        mock.patch('blackhole.config.parse_cmd_args', args), \
        mock.patch('blackhole.config.Config.test'), \
        mock.patch('blackhole.config._compare_uid_and_gid'), \
        mock.patch('blackhole.daemon.Daemon'), \
        mock.patch('atexit.register'), \
        mock.patch('blackhole.supervisor.Supervisor.create'), \
        mock.patch('blackhole.control.setgid'), \
        mock.patch('blackhole.control.setuid'), \
        mock.patch('blackhole.supervisor.Supervisor.run'), \
            pytest.raises(SystemExit) as err:
        run()
    assert str(err.value) == '0'


@pytest.mark.usefixtures('reset_daemon', 'reset_conf', 'cleandir')
def test_run_background():
    cfile = create_config(('listen=127.0.0.1:9000',))
    Config(cfile).load()
    args = Args()

    with mock.patch('sys.argv', ['-c {}'.format(cfile), '-b']), \
        mock.patch('blackhole.config.parse_cmd_args', args), \
        mock.patch('blackhole.config.Config.test'), \
        mock.patch('blackhole.config._compare_uid_and_gid'), \
        mock.patch('blackhole.daemon.Daemon'), \
        mock.patch('atexit.register'), \
        mock.patch('blackhole.supervisor.Supervisor.create'), \
        mock.patch('blackhole.control.setgid'), \
        mock.patch('blackhole.control.setuid'), \
        mock.patch('blackhole.supervisor.Supervisor.run'), \
            pytest.raises(SystemExit) as err:
        run()
    assert str(err.value) == '0'


@pytest.mark.usefixtures('reset_daemon', 'reset_conf', 'cleandir')
def test_run_daemon_create_error():
    cfile = create_config(('listen=127.0.0.1:9000',))
    Config(cfile).load()
    args = Args()

    with mock.patch('sys.argv', ['-c {}'.format(cfile), '-b']), \
        mock.patch('blackhole.config.parse_cmd_args', args), \
        mock.patch('blackhole.config.Config.test'), \
        mock.patch('blackhole.config._compare_uid_and_gid'), \
        mock.patch('atexit.register', side_effect=DaemonException), \
            pytest.raises(SystemExit) as err:
                            run()
    assert str(err.value) == '64'


@pytest.mark.usefixtures('reset_daemon', 'reset_conf', 'cleandir')
def test_run_daemon_daemonize_error():
    pidfile = os.path.join(os.getcwd(), 'nothing.pid')
    cfile = create_config(('listen=127.0.0.1:9000',
                           'pidfile={}'.format(pidfile)))
    Config(cfile).load()
    args = Args()

    with mock.patch('sys.argv', ['-c {}'.format(cfile), '-b']), \
        mock.patch('blackhole.config.parse_cmd_args', args), \
        mock.patch('blackhole.config.Config.test'), \
        mock.patch('blackhole.config._compare_uid_and_gid'), \
        mock.patch('atexit.register'), \
        mock.patch('blackhole.supervisor.Supervisor.create'), \
        mock.patch('blackhole.control.setgid'), \
        mock.patch('blackhole.control.setuid'), \
        mock.patch('blackhole.daemon.Daemon.daemonize',
                   side_effect=DaemonException), \
        mock.patch('blackhole.supervisor.Supervisor.stop'), \
            pytest.raises(SystemExit) as err:
        run()
    assert str(err.value) == '64'
