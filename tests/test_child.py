# (The MIT License)
#
# Copyright (c) 2013-2017 Kura
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# pylama:skip=1

import asyncio
import os
import socket
from unittest import mock

import pytest

from blackhole import protocols
from blackhole.child import Child
from blackhole.control import _socket
from blackhole.streams import StreamProtocol

from ._utils import (Args, cleandir, create_config, create_file, reset)


@pytest.mark.usefixtures('reset', 'cleandir')
def test_initiation():
    Child('', '', [], '1')


@pytest.mark.usefixtures('reset', 'cleandir')
def test_start():
    socks = [{'sock': None, 'ssl': None}, {'sock': None, 'ssl': 'abc'}]
    child = Child('', '', socks, '1')
    with mock.patch('asyncio.Task'), \
        mock.patch('blackhole.child.Child.heartbeat'), \
        mock.patch('asyncio.unix_events._UnixSelectorEventLoop.run_forever'), \
        mock.patch('blackhole.child.Child.stop'), \
            mock.patch('os._exit') as mock_exit:
        child.start()
    assert mock_exit.called is True


@pytest.mark.usefixtures('reset', 'cleandir')
def test_stop():
    socks = [{'sock': None, 'ssl': None}, {'sock': None, 'ssl': 'abc'}]
    child = Child('', '', socks, '1')
    child.loop = mock.MagicMock()
    child.clients.append(mock.MagicMock())
    child.servers.append(mock.MagicMock())
    child.heartbeat_task = mock.MagicMock()
    child.server_task = mock.MagicMock()

    with mock.patch('os._exit') as mock_exit, \
            mock.patch('asyncio.unix_events._UnixSelectorEventLoop.'
                       'run_until_complete'):
        child.stop()
    assert mock_exit.called is True


@pytest.mark.usefixtures('reset', 'cleandir')
def test_stop_runtime_exception():
    socks = [{'sock': None, 'ssl': None}, {'sock': None, 'ssl': 'abc'}]
    child = Child('', '', socks, '1')
    child.loop = mock.MagicMock()
    child.clients.append(mock.MagicMock())
    child.servers.append(mock.MagicMock())
    child.heartbeat_task = mock.MagicMock()
    child.server_task = mock.MagicMock()

    with mock.patch('os._exit') as mock_exit, \
            mock.patch('asyncio.unix_events._UnixSelectorEventLoop.'
                       'stop', side_effect=RuntimeError):
        child.stop()
    assert mock_exit.called is True


@pytest.mark.usefixtures('reset', 'cleandir')
@pytest.mark.asyncio
async def test_start_child_loop(event_loop):
    sock = _socket('127.0.0.1', 0, socket.AF_INET)
    socks = ({'sock': sock, 'ssl': None}, )
    child = Child('', '', socks, '1')
    child.loop = event_loop
    await child._start()
    assert len(child.servers) == 1
    for server in child.servers:
        server.close()


@pytest.mark.usefixtures('reset', 'cleandir')
@pytest.mark.asyncio
async def test_child_heartbeat_not_started(event_loop):
    up_read, up_write = os.pipe()
    down_read, down_write = os.pipe()
    os.close(up_write)
    os.close(down_read)
    child = Child(up_read, down_write, [], '1')
    child.loop = event_loop
    child._started = False
    with mock.patch('asyncio.Task') as mock_task, \
        mock.patch('blackhole.child.Child._start') as mock_start, \
            mock.patch('blackhole.child.Child.stop') as mock_stop:
        await child.heartbeat()
    assert mock_task.called is True
    assert mock_start.called is True
    assert mock_stop.called is True


@pytest.mark.usefixtures('reset', 'cleandir')
@pytest.mark.asyncio
async def test_child_heartbeat_started(event_loop):
    up_read, up_write = os.pipe()
    down_read, down_write = os.pipe()
    os.close(up_write)
    os.close(down_read)
    child = Child(up_read, down_write, [], '1')
    child.loop = event_loop
    child._started = True
    sp = StreamProtocol()
    sp.reader = asyncio.StreamReader()

    async def reset():
        sp.reader.feed_data(protocols.PING)
        child._started = False
    reset_task = asyncio.Task(reset())
    with mock.patch('blackhole.streams.StreamProtocol', return_value=sp), \
        mock.patch('asyncio.Task') as mock_task, \
        mock.patch('blackhole.child.Child._start') as mock_start, \
            mock.patch('blackhole.child.Child.stop') as mock_stop:
        await child.heartbeat()
    reset_task.cancel()
    assert mock_task.called is True
    assert mock_start.called is True
    assert mock_stop.called is True
