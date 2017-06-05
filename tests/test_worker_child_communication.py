import asyncio
import os
import signal
import socket
import time
from unittest import mock

import pytest

from blackhole.control import server
from blackhole.worker import Worker

from ._utils import (Args, cleandir, create_config, create_file, reset_conf,
                     reset_daemon, reset_supervisor)


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
@pytest.mark.asyncio
async def test_ping_pong(unused_tcp_port):
    aserver = server('127.0.0.1', unused_tcp_port, socket.AF_INET)
    started = time.monotonic()
    worker = Worker('1', [aserver, ])
    assert worker._started is True
    await asyncio.sleep(35)
    worker.stop()
    assert worker._started is False
    assert worker.ping > started
    assert worker.ping_count == 2


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
@pytest.mark.asyncio
async def test_restart(unused_tcp_port):
    aserver = server('127.0.0.1', unused_tcp_port, socket.AF_INET)
    started = time.monotonic()
    worker = Worker('1', [aserver, ])
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
