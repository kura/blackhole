import asyncio
import socket

import pytest

from blackhole.control import _socket
from blackhole.worker import Worker

from ._utils import *


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
@pytest.mark.asyncio
async def test_ping_pong():
    sock = _socket('127.0.0.1', 0, socket.AF_INET)
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    worker = Worker('1', [sock, ])
    await asyncio.sleep(30)
    worker.stop()
    for task in asyncio.Task.all_tasks(loop):
        task.cancel()
    assert worker._started is False
