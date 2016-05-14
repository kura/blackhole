import asyncio
import socket

import pytest

from blackhole.control import _socket
from blackhole.worker import Worker


@pytest.mark.asyncio
async def test_worker():
    sock = _socket('127.0.0.1', 0, socket.AF_INET)
    worker = Worker('1', [sock, ])
    await asyncio.sleep(30)
    worker.stop()
    assert worker._started is False
