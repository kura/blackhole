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

"""Provides functionality to spawn and control child processes."""


import asyncio
import logging
import os
import signal

from . import protocols
from .smtp import Smtp
from .streams import StreamProtocol


__all__ = ('Child', )
"""Tuple all the things."""


logger = logging.getLogger('blackhole.child')


class Child:
    """
    A child process.

    Each child process maintains a list of the internal
    :py:class:`asyncio.Server` instances it utilises. Each child also
    maintains a list of all connections being managed by the child.
    """

    _started = False
    servers = []
    """List of :py:class:`asyncio.Server` instances."""

    clients = []
    """List of clients connected to this process."""

    def __init__(self, up_read, down_write, socks, idx):
        """
        Initialise a child process.

        :param int up_read: A file descriptor for reading.
        :param int down_write: A file descriptor for writing.
        :param list socks: A list of sockets.
        """
        self.up_read = up_read
        self.down_write = down_write
        self.socks = socks
        self.idx = idx

    def start(self):
        """Start the child process."""
        logger.debug('Starting child %s', self.idx)
        self._started = True
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        signal.signal(signal.SIGTERM, self.stop)
        self.heartbeat_task = asyncio.Task(self.heartbeat())
        self.loop.run_forever()
        self.stop()
        os._exit(os.EX_OK)

    async def _start(self):
        """Create an asyncio server for each socket."""
        for sock in self.socks:
            server = await self.loop.create_server(lambda: Smtp(self.clients),
                                                   **sock)
            self.servers.append(server)

    def stop(self, *args, **kwargs):
        """
        Stop the child process.

        Mark the process as being stopped, closes each client connected via
        this child, cancels internal communication with the supervisor and
        finally stops the process and exits.
        """
        self._started = False
        self.loop.stop()
        for _ in range(len(self.clients)):
            client = self.clients.pop()
            client.close()
        for _ in range(len(self.servers)):
            server = self.servers.pop()
            server.close()
        self.heartbeat_task.cancel()
        self.server_task.cancel()
        for task in asyncio.Task.all_tasks(self.loop):
            task.cancel()
        self._started = False
        os._exit(os.EX_OK)

    async def heartbeat(self):
        """
        Handle heartbeat between a worker and child.

        If a child process stops communicating with it's worker, it will be
        killed, the worker managing it will also be removed and a new worker
        and child will be spawned.

        .. note::

           3 bytes are used in the communication channel.

           - b'x01' -- :const:`blackhole.protocols.PING`
           - b'x02' -- :const:`blackhole.protocols.PONG`

           These message values are defined in the :mod:`blackhole.protocols`
           schema. Documentation is available at --
           https://kura.github.io/blackhole/api-protocols.html#blackhole.protocols
        """
        read_fd = os.fdopen(self.up_read, 'rb')
        r_trans, r_proto = await self.loop.connect_read_pipe(StreamProtocol,
                                                             read_fd)
        write_fd = os.fdopen(self.down_write, 'wb')
        w_trans, w_proto = await self.loop.connect_write_pipe(StreamProtocol,
                                                              write_fd)
        reader = r_proto.reader
        writer = asyncio.StreamWriter(w_trans, w_proto, reader, self.loop)
        self.server_task = asyncio.Task(self._start())

        while self._started:
            try:
                msg = await reader.read(3)
            except:  # noqa
                break
            if msg == protocols.PING:
                logger.debug('child.%s.heartbeat: Ping request received from '
                             'parent', self.idx)
                writer.write(protocols.PONG)
            await asyncio.sleep(5)
        r_trans.close()
        w_trans.close()
        self.stop()
