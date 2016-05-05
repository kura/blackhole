# (The MIT License)
#
# Copyright (c) 2016 Kura
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

"""
blackhole.worker.

This module houses functionality to control child processes.
"""


import asyncio
import logging
import signal
import time
import os

from blackhole.child import Child
from blackhole.control import setgid, setuid


logger = logging.getLogger('blackhole.worker')


class Worker:
    """A worker."""

    _started = False

    def __init__(self, socks, loop=None):
        """
        Initialise the worker.

        :param loop:
        :type loop: :any:`asyncio.unix_events._UnixSelectorEventLoop`
        :param socks: a list of sockets.
        :type socks: :any:`list`
        """
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        self.socks = socks
        self.start()

    def start(self):
        """Create and fork off child procresses."""
        assert not self._started
        self._started = True

        up_read, up_write = os.pipe()
        down_read, down_write = os.pipe()

        logger.debug('Forking')
        self.pid = os.fork()
        if self.pid:  # Parent
            os.close(up_read)
            os.close(down_write)
            asyncio.async(self.connect(self.pid, up_write, down_read))
        else:  # Child
            os.close(up_write)
            os.close(down_read)
            # Make sure we change our permissions if required.
            setgid()
            setuid()
            asyncio.set_event_loop(None)
            process = Child(up_read, down_write, self.socks)
            process.start()

    async def connect(self, pid, up_write, down_read):
        """
        Connect the children and supervisor so they can communicate.

        :param pid: a process identifier
        :type pid:
        :param up_write: a file descriptor
        :type up_write:
        :param down_read: a file descriptor
        :type down_read:
        """
        r_trans, r_proto = await self.loop.connect_read_pipe(
            asyncio.StreamReaderProtocol, os.fdopen(down_read, 'rb'))
        w_trans, w_proto = await self.loop.connect_write_pipe(
            asyncio.StreamReaderProtocol, os.fdopen(up_write, 'wb'))

        self.pid = pid
        self.ping = time.monotonic()
        self.rtransport = r_trans
        self.wtransport = w_trans

    def kill(self):
        """Terminate a child process."""
        os.kill(self.pid, signal.SIGTERM)
