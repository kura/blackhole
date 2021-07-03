# -*- coding: utf-8 -*-

# (The MIT License)
#
# Copyright (c) 2013-2021 Kura
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


import asyncio
import socket
import time

import pytest

from blackhole.control import server
from blackhole.worker import Worker


from ._utils import (  # noqa: F401; isort:skip
    Args,
    cleandir,
    create_config,
    create_file,
    reset,
)


try:
    import uvloop  # noqa
except ImportError:
    pass


@pytest.mark.usefixtures("reset", "cleandir")
@pytest.mark.asyncio
@pytest.mark.slow
async def test_worker_ping_pong(unused_tcp_port, event_loop):
    aserver = server("127.0.0.1", unused_tcp_port, socket.AF_INET)
    started = time.monotonic()
    worker = Worker("1", [aserver], loop=event_loop)
    assert worker._started is True
    await asyncio.sleep(35)
    worker.stop()
    assert worker._started is False
    assert worker.ping > started
    assert worker.ping_count == 2
    aserver["sock"].close()


@pytest.mark.usefixtures("reset", "cleandir")
@pytest.mark.asyncio
@pytest.mark.slow
async def test_restart(unused_tcp_port, event_loop):
    aserver = server("127.0.0.1", unused_tcp_port, socket.AF_INET)
    started = time.monotonic()
    worker = Worker("1", [aserver], loop=event_loop)
    assert worker._started is True
    await asyncio.sleep(25)
    worker.ping = time.monotonic() - 120
    old_pid = worker.pid
    await asyncio.sleep(15)
    assert worker.pid is not old_pid
    worker.stop()
    assert worker._started is False
    assert worker.ping > started
    assert worker.ping_count == 0
    aserver["sock"].close()
