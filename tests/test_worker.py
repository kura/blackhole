import asyncio
import os
import time
from io import BytesIO
from unittest import mock

import pytest

from blackhole import protocols
from blackhole.config import Config
from blackhole.worker import Worker

from ._utils import (Args, cleandir, create_config, create_file, reset_conf,
                     reset_daemon, reset_supervisor)


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
@pytest.mark.asyncio
async def test_start_stop():
    worker = Worker(1, [])
    assert worker._started is True
    await asyncio.sleep(10)
    worker.stop()
    assert worker._started is False


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_child_start_setgid_fails_invalid_group():
    cfile = create_config(('user=fgqewgreghrehgerhehw',
                           'group=fgqewgreghrehgerhehw'))
    Config(cfile).load()
    with mock.patch('os.pipe', return_value=('', '')), \
        mock.patch('os.fork', return_value=False), \
        mock.patch('os.close'), \
        mock.patch('os.setgid', side_effect=KeyError), \
            pytest.raises(SystemExit) as err:
        Worker([], [])
    assert str(err.value) == '64'


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_child_start_setgid_fails_permissions():
    cfile = create_config(('user=fgqewgreghrehgerhehw',
                           'group=fgqewgreghrehgerhehw'))
    Config(cfile).load()
    with mock.patch('os.pipe', return_value=('', '')), \
        mock.patch('os.fork', return_value=False), \
        mock.patch('os.close'), \
        mock.patch('os.setgid', side_effect=PermissionError), \
            pytest.raises(SystemExit) as err:
        Worker([], [])
    assert str(err.value) == '64'


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_child_start_setuid_fails_invalid_user():
    cfile = create_config(('user=fgqewgreghrehgerhehw',
                           'group=fgqewgreghrehgerhehw'))
    Config(cfile).load()
    with mock.patch('os.pipe', return_value=('', '')), \
        mock.patch('os.fork', return_value=False), \
        mock.patch('os.close'), \
        mock.patch('os.setuid', side_effect=KeyError), \
            pytest.raises(SystemExit) as err:
        Worker([], [])
    assert str(err.value) == '64'


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_child_start_setuid_fails_permissions():
    cfile = create_config(('user=fgqewgreghrehgerhehw',
                           'group=fgqewgreghrehgerhehw'))
    Config(cfile).load()
    with mock.patch('os.pipe', return_value=('', '')), \
        mock.patch('os.fork', return_value=False), \
        mock.patch('os.close'), \
        mock.patch('os.setuid', side_effect=PermissionError), \
            pytest.raises(SystemExit) as err:
        Worker([], [])
    assert str(err.value) == '64'
