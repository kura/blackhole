# -*- coding: utf-8 -*-

# (The MIT License)
#
# Copyright (c) 2013-2021 Kura
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

"""Communication protocols used by the worker and child processes."""


import asyncio
import logging

from .config import Config


__all__ = ("StreamReaderProtocol", "PING", "PONG")
"""Tuple all the things."""


logger = logging.getLogger("blackhole.protocols")


PING = b"x01"
"""Protocol message used by the worker and child processes to communicate."""

PONG = b"x02"
"""Protocol message used by the worker and child processes to communicate."""


class StreamReaderProtocol(asyncio.StreamReaderProtocol):
    """The class responsible for handling connections commands."""

    def __init__(self, clients, loop=None):
        """
        Initialise the protocol.

        :param list clients: A list of connected clients.
        :param loop: The event loop to use.
        :type loop: :py:obj:`None` or
                    :py:class:`syncio.unix_events._UnixSelectorEventLoop`
        """
        logger.debug("init")
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        logger.debug("loop")
        super().__init__(
            asyncio.StreamReader(loop=self.loop),
            client_connected_cb=self._client_connected_cb,
            loop=self.loop,
        )
        logger.debug("super")
        self.clients = clients
        self.config = Config()
        logger.debug(self.config)
        # This is not a nice way to do this but, socket.getfqdn silently fails
        # and crashes inbound connections when called after os.fork
        self.fqdn = self.config.mailname

    def flags_from_transport(self):
        """Adapt internal flags for the transport in use."""
        # This has to be done here since passing it as part of init causes
        # flags to become garbled and mixed up. Artifact of loop.create_server
        sock = self.transport.get_extra_info("socket")
        # Ideally this would use transport.get_extra_info('sockname') but that
        # crashes the child process for some weird reason. Getting the socket
        # and interacting directly does not cause a crash, hence...
        sock_name = sock.getsockname()
        flags = self.config.flags_from_listener(sock_name[0], sock_name[1])
        if len(flags.keys()) > 0:
            self._flags = flags
            self._disable_dynamic_switching = True
            logger.debug("Flags enabled, disabling dynamic switching")
            logger.debug(f"Flags for this connection: {self._flags}")

    def _client_connected_cb(self, reader, writer):
        """
        Bind a stream reader and writer to the SMTP Protocol.

        :param asyncio.streams.StreamReader reader: An object for reading
                                                    incoming data.
        :param asyncio.streams.StreamWriter writer: An object for writing
                                                    outgoing data.
        """
        self._reader = reader
        self._writer = writer
        self.clients.append(writer)

    def connection_lost(self, exc):
        """
        Client connection is closed or lost.

        :param exc exc: Exception.
        """
        logger.debug("Peer disconnected")
        super().connection_lost(exc)
        self.connection_closed, self._connection_closed = True, True
        try:
            self.clients.remove(self._writer)
        except ValueError:
            pass

    async def wait(self):
        """
        Wait for data from the client.

        :returns: A line of received data.
        :rtype: :py:obj:`str`

        .. note::

           Also handles client timeouts if they wait too long before sending
           data. -- https://kura.gg/blackhole/configuration.html#timeout
        """
        while not self.connection_closed:
            try:
                line = await asyncio.wait_for(
                    self._reader.readline(),
                    self.config.timeout,
                )
            except asyncio.TimeoutError:
                await self.timeout()
                return None
            return line

    async def close(self):
        """Close the connection from the client."""
        logger.debug("Closing connection")
        if self._writer:
            try:
                self.clients.remove(self._writer)
            except ValueError:
                pass
            self._writer.close()
            await self._writer.drain()
        self._connection_closed = True

    async def push(self, msg):
        """
        Write a response message to the client.

        :param str msg: The message for the SMTP code
        """
        response = f"{msg}\r\n".encode("utf-8")
        logger.debug(f"SEND {response}")
        self._writer.write(response)
        await self._writer.drain()
