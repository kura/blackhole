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
blackhole.child.

This module houses the functionality to spawn child processes.
"""


import asyncio
import logging
import os
import signal

from blackhole.smtp import Smtp
from blackhole.streams import StreamProtocol


logger = logging.getLogger('blackhole.child')


class Child:
    """A child process."""

    def __init__(self, up_read, down_write, socks):
        """
        Initialise a child process.

        :param up_read:
        :type up_read: :any:`os.pipe`
        :param down_write:
        :type down_write: :any:`os.pipe`
        :param socks: a list of sockets
        :type socks: :any:`list`
        """
        self.up_read = up_read
        self.down_write = down_write
        self.socks = socks
        self.clients = []

    def start(self):
        """Start the child process."""
        self.loop = loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        def stop():
            """Stop the child process."""
            for client in self.clients:
                client.close()
            self.loop.stop()
            os._exit(0)
        loop.add_signal_handler(signal.SIGINT, stop)

        asyncio.Task(self.heartbeat())
        asyncio.get_event_loop().run_forever()
        os._exit(0)

    async def _start(self, writer):
        """
        Spawn each asyncio 'server' for each socket.

        :param writer:
        :type writer: :any:`asyncio.StreamWriter`
        """
        for sock in self.socks:
            ctx = sock['context'] if 'context' in sock else None
            sock = sock['sock']
            await self.loop.create_server(lambda: Smtp(writer, self.clients),
                                          sock=sock, ssl=ctx)

    async def heartbeat(self):
        """Handle heartbeat between a worker and child."""
        r_trans, r_proto = await self.loop.connect_read_pipe(
            StreamProtocol, os.fdopen(self.up_read, 'rb'))
        w_trans, w_proto = await self.loop.connect_write_pipe(
            StreamProtocol, os.fdopen(self.down_write, 'wb'))

        reader = r_proto.reader
        writer = asyncio.StreamWriter(w_trans, w_proto, reader, self.loop)
        asyncio.Task(self._start(writer))

        while True:
            try:
                msg = await reader.readline()
            except:
                self.loop.stop()
                break
            if msg == b'0x1\n':
                await writer.write(b'0x2\n')
            elif msg == b'0x0\n':
                for client in self.clients:
                    client.close()
                break
        r_trans.close()
        w_trans.close()
