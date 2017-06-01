import asyncio
import os
import socket
from unittest import mock

import pytest

from blackhole.streams import StreamProtocol

from ._utils import (Args, cleandir, create_config, create_file, reset_conf,
                     reset_daemon, reset_supervisor)


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
@pytest.mark.asyncio
async def test_client_not_connected():
    sp = StreamProtocol()
    assert sp.is_connected() is False


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
@pytest.mark.asyncio
async def test_client_connected(event_loop):
    sp = StreamProtocol(loop=event_loop)
    sp.connection_made(asyncio.Transport())
    assert sp.is_connected() is True


# @pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
#         'cleandir')
# @pytest.mark.asyncio
# async def test_connection_lost_exception(event_loop):
#     sp = StreamProtocol(loop=event_loop)
#     sp.connection_made(asyncio.Transport())
#     assert sp.is_connected() is True
#     with pytest.raises(KeyError):
#         sp.connection_lost(KeyError)
