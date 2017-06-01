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

"""Provides additional stream classes."""

import asyncio
import logging


__all__ = ('StreamProtocol', )
"""Tuple all the things."""


logger = logging.getLogger('blackhole.streams')


class StreamProtocol(asyncio.streams.FlowControlMixin, asyncio.Protocol):
    """Helper class to adapt between Protocol and StreamReader."""

    def __init__(self, *, loop=None, disconnect_error=RuntimeError, **kwargs):
        """Stream protocol."""
        super().__init__(loop=loop)
        self.transport = None
        self.writer = None
        self.reader = asyncio.StreamReader(loop=loop)

    def is_connected(self):
        """Client is connected."""
        return self.transport is not None

    def connection_made(self, transport):
        """Client connection made callback."""
        self.transport = transport
        self.reader.set_transport(transport)
        self.writer = asyncio.StreamWriter(transport, self, self.reader,
                                           self._loop)

    def connection_lost(self, exc):
        """Client connection lost callback."""
        self.transport = self.writer = None
        self.reader._transport = None

        logger.debug(exc)
        if exc is None:
            self.reader.feed_eof()
        else:
            self.reader.set_exception(exc)

        super().connection_lost(exc)

    def data_received(self, data):
        """Client data received."""
        self.reader.feed_data(data)

    def eof_received(self):
        """Client EOF received."""
        self.reader.feed_eof()
