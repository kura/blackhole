import asyncio
import os
from io import BytesIO
import time
from unittest import mock

import pytest

from blackhole import protocols
from blackhole.config import Config
from blackhole.worker import Worker

from ._utils import (cleandir, reset_conf, reset_daemon, reset_supervisor,
                     create_config, create_file, Args)


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_init_start():
    with mock.patch('blackhole.worker.Worker.start') as mock_start:
        Worker([], [])
    assert mock_start.called is True


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_stop():
    with mock.patch('blackhole.worker.Worker.start') as mock_start, \
            mock.patch('os.kill') as mock_kill:
        w = Worker([], [])
        w.chat_task = mock.Mock()
        w.heartbeat_task = mock.Mock()
        w.rtransport = mock.Mock()
        w.wtransport = mock.Mock()
        w.pid = 123
        w.stop()
    assert mock_start.called is True
    assert mock_kill.called is True


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_stop_runtime_exception():
    with mock.patch('blackhole.worker.Worker.start') as mock_start, \
            mock.patch('os.kill', side_effect=ProcessLookupError):
        w = Worker([], [])
        w.chat_task = mock.Mock()
        w.heartbeat_task = mock.Mock()
        w.rtransport = mock.Mock()
        w.wtransport = mock.Mock()
        w.pid = 123
        w.stop()
    assert mock_start.called is True


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_parent_start():
    with mock.patch('os.pipe', return_value=('', '')) as mock_pipe, \
        mock.patch('os.fork', return_value=123) as mock_fork, \
        mock.patch('os.close') as mock_close, \
        mock.patch('asyncio.ensure_future') as mock_async, \
            mock.patch('blackhole.worker.Worker.connect') as mock_connect:
        w = Worker([], [])
        w.pid = 123
    assert mock_pipe.call_count == 2
    assert mock_fork.called is True
    assert mock_close.call_count == 2
    assert mock_async.called is True
    assert mock_connect.called is True


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_child_start():
    with mock.patch('os.fork', return_value=-1) as mock_fork, \
        mock.patch('blackhole.control.setgid'), \
        mock.patch('blackhole.control.setuid'), \
        mock.patch('asyncio.Task'), \
        mock.patch('blackhole.child.Child.heartbeat'), \
        mock.patch('asyncio.unix_events._UnixSelectorEventLoop.run_forever'), \
        mock.patch('blackhole.child.Child.stop'), \
            mock.patch('os._exit') as mock_exit:
        Worker([], [])
    assert mock_fork.called is True
    assert mock_exit.called is True


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


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
@pytest.mark.asyncio
async def test_worker_heartbeat_not_started(event_loop):
    with mock.patch('blackhole.worker.Worker.start') as mock_start:
        worker = Worker('1', [])
    assert mock_start.called is True
    worker._started = False
    with mock.patch('blackhole.worker.Worker.start') as mock_heartbeat_start, \
            mock.patch('blackhole.worker.Worker.stop') as mock_heartbeat_stop:
        await worker.heartbeat(None)
    assert mock_heartbeat_start.called is False
    assert mock_heartbeat_stop.called is False


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
@pytest.mark.asyncio
async def test_worker_heartbeat_started_bad_ping(event_loop):
    with mock.patch('blackhole.worker.Worker.start') as mock_start:
        worker = Worker('1', [])
    assert mock_start.called is True
    worker._started = True
    worker.ping = time.monotonic() - 120
    with mock.patch('blackhole.worker.Worker.start') as mock_heartbeat_start, \
            mock.patch('blackhole.worker.Worker.stop') as mock_heartbeat_stop:
        await worker.heartbeat(None)
    assert mock_heartbeat_start.called is True
    assert mock_heartbeat_stop.called is True


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
@pytest.mark.asyncio
async def test_worker_heartbeat_started_good_ping(event_loop):
    with mock.patch('blackhole.worker.Worker.start') as mock_start:
        worker = Worker('1', [])
    assert mock_start.called is True
    worker._started = True
    worker.ping = time.monotonic() + 120
    writer = BytesIO()
    async def reset():
        await asyncio.sleep(20)
        worker._started = False
    reset_task = asyncio.Task(reset())
    await worker.heartbeat(writer)
    assert worker._started is False
    reset_task.cancel()


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
@pytest.mark.asyncio
async def test_worker_chat_not_started(event_loop):
    with mock.patch('blackhole.worker.Worker.start') as mock_start:
        worker = Worker('1', [])
    assert mock_start.called is True
    worker._started = False
    with mock.patch('blackhole.worker.Worker.start') as mock_chat_start, \
            mock.patch('blackhole.worker.Worker.stop') as mock_chat_stop:
        await worker.chat(None)
    assert mock_chat_start.called is False
    assert mock_chat_stop.called is False


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
@pytest.mark.asyncio
async def test_worker_chat_started_restart(event_loop):
    with mock.patch('blackhole.worker.Worker.start') as mock_start:
        worker = Worker('1', [])
    assert mock_start.called is True
    worker._started = True
    with mock.patch('blackhole.worker.Worker.start') as mock_chat_start, \
        mock.patch('blackhole.worker.Worker.stop') as mock_chat_stop, \
            mock.patch('asyncio.StreamReader.read', side_effect=Exception):
        reader = asyncio.StreamReader()
        await worker.chat(reader)
    assert mock_chat_start.called is True
    assert mock_chat_stop.called is True


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
@pytest.mark.asyncio
async def test_worker_chat_started_good_message(event_loop):
    with mock.patch('blackhole.worker.Worker.start') as mock_start:
        worker = Worker('1', [], loop=event_loop)
    assert mock_start.called is True
    worker._started = True
    worker.ping = 987654321
    reader = asyncio.StreamReader()
    async def reset():
        reader.feed_data(protocols.PONG)
        worker._started = False
    reset_task = asyncio.Task(reset())
    with mock.patch('time.monotonic', return_value=123456789):
        await worker.chat(reader)
    assert worker._started is False
    assert worker.ping == 123456789
    reset_task.cancel()


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
@pytest.mark.asyncio
async def test_worker_connect(event_loop):
    up_read, up_write = os.pipe()
    down_read, down_write = os.pipe()
    os.close(up_read)
    os.close(down_write)
    with mock.patch('blackhole.worker.Worker.start') as mock_start:
        worker = Worker('1', [])
    assert mock_start.called is True
    with mock.patch('asyncio.ensure_future'), \
        mock.patch('blackhole.worker.Worker.chat') as mock_chat, \
            mock.patch('blackhole.worker.Worker.heartbeat') as mock_heartbeat:
        await worker.connect('1', up_write, down_read)
    assert mock_chat.called is True
    assert mock_heartbeat.called is True
