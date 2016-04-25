import os
import tempfile
from unittest import mock

import pytest

from blackhole.application import run
from blackhole.config import Config, Singleton
from blackhole.exceptions import ConfigException, DaemonException


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


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_run_test():
    cfile = create_config(('', ))
    with mock.patch('sys.argv', ['blackhole', '-t', '-c', cfile]):
        with mock.patch('blackhole.config.Config.test_port', return_value=True):
            with pytest.raises(SystemExit) as err:
                run()
    assert str(err.value) == '0'


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_run_test_fails():
    cfile = create_config(('listen=127.0.0.1:0', ))
    with mock.patch('sys.argv', ['blackhole', '-t', '-c', cfile]):
        with pytest.raises(SystemExit) as err:
            run()
    assert str(err.value) == '64'

@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_run_load_test_fails():
    cfile = create_config(('listen=127.0.0.1:0', ))
    with mock.patch('sys.argv', ['blackhole', '-t', '-c', cfile]):
        with mock.patch('blackhole.config.Config.test', side_effect=ConfigException()):
            with pytest.raises(SystemExit) as err:
                run()
    assert str(err.value) == '64'


class Args(object):
    pass


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_run_foreground():
    cfile = create_config(('listen=127.0.0.1:9000',))
    conf = Config(cfile).load()
    args = Args()

    # This is fucking INSANE...
    with mock.patch('sys.argv', ['-c {}'.format(cfile)]):
        with mock.patch('blackhole.config.parse_cmd_args', args):
            with mock.patch('blackhole.config.Config.test'):
                with mock.patch('asyncio.get_event_loop'):
                    with mock.patch('blackhole.control.start_servers'):
                        with mock.patch('blackhole.control.setgid'):
                            with mock.patch('blackhole.control.setuid'):
                                with mock.patch('blackhole.control.stop_servers'):
                                    with mock.patch('asyncio.unix_events._UnixSelectorEventLoop.run_forever'):
                                        with pytest.raises(SystemExit) as err:
                                            run()
    assert str(err.value) == '0'


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_run_background():
    pid = '{}/backhole.pid'.format(os.getcwd())
    cfile = create_config(('listen=127.0.0.1:9000', 'pidfile={}'.format(pid)))
    conf = Config(cfile).load()
    args = Args()

    # This is fucking INSANE...
    with mock.patch('sys.argv', ['-c {}'.format(cfile), '-b']):
        with mock.patch('blackhole.config.parse_cmd_args', args):
            with mock.patch('blackhole.config.Config.test'):
                with mock.patch('asyncio.get_event_loop'):
                    with mock.patch('blackhole.control.start_servers'):
                        with mock.patch('blackhole.control.setgid'):
                            with mock.patch('blackhole.control.setuid'):
                                with mock.patch('blackhole.daemon.Daemon.daemonize') as daemon:
                                    with mock.patch('blackhole.control.stop_servers'):
                                        with mock.patch('asyncio.unix_events._UnixSelectorEventLoop.run_forever'):
                                            with pytest.raises(SystemExit) as err:
                                                run()
    assert str(err.value) == '0'
    assert daemon.called is True


@pytest.mark.usefixtures('reset_conf', 'cleandir')
def test_run_daemon_error():
    pid = '{}/backhole.pid'.format(os.getcwd())
    cfile = create_config(('listen=127.0.0.1:9000', 'pidfile={}'.format(pid)))
    conf = Config(cfile).load()
    args = Args()

    # This is fucking INSANE...
    with mock.patch('sys.argv', ['-c {}'.format(cfile), '-b']):
        with mock.patch('blackhole.config.parse_cmd_args', args):
            with mock.patch('blackhole.config.Config.test'):
                with mock.patch('asyncio.get_event_loop'):
                    with mock.patch('blackhole.control.start_servers'):
                        with mock.patch('blackhole.control.setgid'):
                            with mock.patch('blackhole.control.setuid'):
                                with mock.patch('blackhole.daemon.Daemon.daemonize', side_effect=DaemonException):
                                    with pytest.raises(SystemExit) as err:
                                        run()
    assert str(err.value) == '64'
