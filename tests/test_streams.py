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

from blackhole.streams import StreamProtocol

from ._utils import (Args, cleandir, create_config, create_file, reset)


@pytest.mark.usefixtures('reset', 'cleandir')
@pytest.mark.asyncio
async def test_client_not_connected():
    sp = StreamProtocol()
    assert sp.is_connected() is False


@pytest.mark.usefixtures('reset', 'cleandir')
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
