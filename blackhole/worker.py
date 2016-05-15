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

"""Provides functionality to manage child processes from the supervisor."""


import asyncio
import logging
import os
import signal
import time

from . import protocols
from .child import Child
from .control import setgid, setuid
from .streams import StreamProtocol


__all__ = ('Worker', )


logger = logging.getLogger('blackhole.worker')


class Worker:
    """
    A worker.

    Providers functionality to manage a single child process. The worker is
    responsible for communicating heartbeat information with it's child
    process and starting, stopping and restarting a child as required or
    instructed.
    """

    _started = False

    def __init__(self, idx, socks, loop=None):
        """
        Initialise the worker.

        :param idx: The number reference of the worker and child.
        :type idx: :any:`str`
        :param socks: Sockets to listen for connections on.
        :type socks: :any:`list`
        :param loop: The event loop to use.
        :type loop: :any:`asyncio.unix_events._UnixSelectorEventLoop` or
                    :any:`None` to get the current event loop using
                    :any:`asyncio.get_event_loop`.
        """
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        self.socks = socks
        self.idx = idx
        self.start()

    def start(self):
        """Create and fork off a child process for the current worker."""
        assert not self._started
        self._started = True

        up_read, up_write = os.pipe()
        down_read, down_write = os.pipe()

        self.pid = os.fork()
        if self.pid > 0:  # Parent
            os.close(up_read)
            os.close(down_write)
            asyncio.ensure_future(self.connect(self.pid, up_write, down_read))
        else:  # Child
            os.close(up_write)
            os.close(down_read)
            setgid()
            setuid()
            asyncio.set_event_loop(None)
            process = Child(up_read, down_write, self.socks, self.idx)
            process.start()

    async def heartbeat(self, writer):
        """
        Handle heartbeat between a worker and child.

        If a child process stops communicating with it's worker, it will be
        killed, the worker managing it will also be removed and a new worker
        and child will be spawned.

        :param writer: An object for writing data to the pipe.
        :type writer: :any:`asyncio.StreamWriter`

        .. note::

           3 bytes are used in the communication channel.

           - b'x01' -- :any:`blackhole.protocols.PING`
           - b'x02' -- :any:`blackhole.protocols.PONG`

           The worker will sleep for 15 seconds, before requesting a ping from
           the child. If we go for over 30 seconds waiting for a ping, the
           worker will restart itself and the child bound to it.

           These message values are defined in the :any:`blackhole.protocols`
           schema. Documentation is available at --
           https://blackhole.io/api-protocols.html#blackhole.proto
        """
        while self._started:
            await asyncio.sleep(15)
            if (time.monotonic() - self.ping) < 30:
                writer.write(protocols.PING)
            else:
                if self._started:
                    logger.debug('worker.%s.heartbeat: Communication failed. '
                                 'Restarting worker', self.idx)
                    self.stop()
                    self.start()
                return

    async def chat(self, reader):
        """
        Communicate between a worker and child.

        If a child process stops communicating with it's worker, it will be
        killed, the worker managing it will also be removed and a new worker
        and child will be spawned.

        :param reader: An object for reading data from the pipe.
        :type reader: :any:`asyncio.StreamReader`

        .. note::

           3 bytes are used in the communication channel.

           - b'x01' -- :any:`blackhole.protocols.PING`
           - b'x02' -- :any:`blackhole.protocols.PONG`

           Read data coming in from the child. If a PONG is received, we'll
           update the worker, setting this PONG as a 'PING' from the child.

           These message values are defined in the :any:`blackhole.proto`
           schema. Documentation is available at --
           https://blackhole.io/api-protocols.html#blackhole.proto
        """
        while self._started:
            try:
                msg = await reader.read(3)
            except:
                if self._started:
                    logger.debug('worker.%s.chat: Communication failed. '
                                 'Restarting worker', self.idx)
                    self.stop()
                    self.start()
                return
            if msg == protocols.PONG:
                logger.debug('worker.%s.chat: Ping received from child',
                             self.idx)
                self.ping = time.monotonic()

    async def connect(self, pid, up_write, down_read):
        """
        Connect the child and worker so they can communicate.

        :param pid: A process identifier
        :type pid: :any:`int`
        :param up_write: a file descriptor
        :type up_write: :any:`io.TextIOWrapper`
        :param down_read: a file descriptor
        :type down_read: :any:`io.TextIOWrapper`
        """
        read_fd = os.fdopen(down_read, 'rb')
        r_trans, r_proto = await self.loop.connect_read_pipe(StreamProtocol,
                                                             read_fd)
        write_fd = os.fdopen(up_write, 'wb')
        w_trans, w_proto = await self.loop.connect_write_pipe(StreamProtocol,
                                                              write_fd)
        reader = r_proto.reader
        writer = asyncio.StreamWriter(w_trans, w_proto, reader, self.loop)
        self.pid = pid
        self.ping = time.monotonic()
        self.rtransport = r_trans
        self.wtransport = w_trans
        self.chat_task = asyncio.ensure_future(self.chat(reader))
        self.heartbeat_task = asyncio.ensure_future(self.heartbeat(writer))

    def stop(self):
        """Terminate the worker and it's respective child process."""
        self._started = False
        self.chat_task.cancel()
        self.heartbeat_task.cancel()
        self.rtransport.close()
        self.wtransport.close()
        for task in asyncio.Task.all_tasks(self.loop):
            task.cancel()
        try:
            os.kill(self.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
