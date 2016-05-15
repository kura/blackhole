import asyncio
import socket

import pytest

from blackhole.control import server
from blackhole.worker import Worker

from ._utils import (cleandir, reset_conf, reset_daemon, reset_supervisor,
                     create_config, create_file, Args)


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
@pytest.mark.asyncio
async def test_ping_pong():
    aserver = server('127.0.0.1', 0, socket.AF_INET)
    worker = Worker('1', [aserver, ])
    await asyncio.sleep(35)
    worker.stop()
    assert worker._started is False
