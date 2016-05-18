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
Communication protocols used by the worker and child processes to
communicate.
"""

import asyncio
import logging

from . config import Config


__all__ = ('PING', 'PONG', 'Protocol')


PING = b'x01'
"""Protocol message used by the worker and child processes to communicate."""
PONG = b'x02'
"""Protocol message used by the worker and child processes to communicate."""


logger = logging.getLogger('blackhole.protocol')


class Protocol(asyncio.StreamReaderProtocol):

    fqdn = 'blackhole.io'
    flags = {}

    def __init__(self, clients, flags, loop=None):
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        super().__init__(asyncio.StreamReader(loop=self.loop),
                         client_connected_cb=self._client_connected_cb,
                         loop=self.loop)
        self.clients = clients
        self.config = Config()
        # This is not a nice way to do this but, socket.getfqdn silently fails
        # and craches inbound connections when called after os.fork
        self.flags = flags
        self.fqdn = self.config.mailname

    def connection_made(self, transport):
        """
        Tie a connection to the protocol.

        :param transport: The transport class.
        :type transport: :any:`asyncio.transport.Transport`
        """
        super().connection_made(transport)
        logger.debug('Peer connected')
        self.transport = transport
        self.connection_closed = False
        self._handler_coroutine = self.loop.create_task(self._handle_client())

    def _client_connected_cb(self, reader, writer):
        """
        Callback that binds a stream reader and writer to the SMTP Protocol.

        :param reader: An object for reading incoming data.
        :type reader: :any:`asyncio.streams.StreamReader`
        :param writer: An object for writing outgoing data.
        :type writer: :any:`asyncio.streams.StreamWriter`
        """
        self._reader = reader
        self._writer = writer
        self.clients.append(writer)

    def connection_lost(self, exc):
        """
        Callback for when a connection is closed or lost.

        :param exc:
        :type exc:
        """
        logger.debug('Peer disconnected')
        try:
            self.clients.remove(self._writer)
        except ValueError:
            pass
        super().connection_lost(exc)
        self._connection_closed = True

    async def close(self):
        """Close the connection from the client."""
        logger.debug('Closing connection')
        if self._writer:
            try:
                self.clients.remove(self._writer)
            except ValueError:
                pass
            self._writer.close()
            await self._writer.drain()
        self._connection_closed = True
