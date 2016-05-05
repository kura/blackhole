import asyncio
import logging
import os
import tempfile
from unittest import mock

import pytest

from blackhole.worker import Worker


logging.getLogger('blackhole').addHandler(logging.NullHandler())


@pytest.fixture()
def cleandir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)


def test_init_start():
    with mock.patch('blackhole.worker.Worker.start') as mock_start:
        Worker([], [])
    assert mock_start.called is True


def test_kill():
    with mock.patch('blackhole.worker.Worker.start') as mock_start, \
            mock.patch('os.kill') as mock_kill:
        w = Worker([], [])
        w.pid = 123
        w.kill()
    assert mock_start.called is True
    assert mock_kill.called is True


def test_parent_start():
    with mock.patch('os.pipe', return_value=('', '')) as mock_pipe, \
        mock.patch('os.fork', return_value=123) as mock_fork, \
        mock.patch('os.close') as mock_close, \
        mock.patch('asyncio.async') as mock_async, \
            mock.patch('blackhole.worker.Worker.connect') as mock_connect:
        w = Worker([], [])
        w.pid = 123
    assert mock_pipe.call_count == 2
    assert mock_fork.called is True
    assert mock_close.call_count == 2
    assert mock_async.called is True
    assert mock_connect.called is True


def test_child_start():
    with mock.patch('os.pipe', return_value=('', '')) as mock_pipe, \
        mock.patch('os.fork', return_value=False) as mock_fork, \
        mock.patch('os.close') as mock_close, \
        mock.patch('asyncio.new_event_loop'), \
        mock.patch('asyncio.set_event_loop'), \
        mock.patch('asyncio.unix_events._UnixSelectorEventLoop.'
                   'create_server'), \
        mock.patch('asyncio.unix_events._UnixSelectorEventLoop.'
                   'run_until_complete'), \
        mock.patch('asyncio.async'), \
        mock.patch('asyncio.unix_events._UnixSelectorEventLoop.run_forever'), \
            mock.patch('os._exit') as mock_exit:
        Worker([], [])
    assert mock_pipe.call_count == 2
    assert mock_fork.called is True
    assert mock_close.call_count == 2
    assert mock_exit.called is True


@pytest.mark.usefixtures('cleandir')
@pytest.mark.asyncio
async def test_connect():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with mock.patch('os.fork', return_value=123):
        Worker(loop, [])
