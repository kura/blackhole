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


import asyncio
import socket

from blackhole.config import Config
from blackhole.utils import (mailname, message_id)


class Smtp(asyncio.StreamReaderProtocol):

    def __init__(self, *args, **kwargs):
        self.loop = asyncio.get_event_loop()
        super().__init__(
            asyncio.StreamReader(loop=self.loop),
            client_connected_cb=self._client_connected_cb,
            loop=self.loop)
        self.config = Config()
        self.fqdn = mailname()
        self.message_id = message_id()

    def connection_made(self, transport):
        super().connection_made(transport)
        self.transport = transport
        self.connection_closed = False
        self._handler_coroutine = self.loop.create_task(self._handle_client())

    def _client_connected_cb(self, reader, writer):
        self._reader = reader
        self._writer = writer

    def connection_lost(self, exc):
        self._connection_closed = True
        super().connection_lost(exc)

    async def _handle_client(self):
        await self.greet()
        while not self.connection_closed:
            line = await self._reader.readline()
            line = line.decode('utf-8').rstrip('\r\n')
            parts = line.split(None, 1)
            if parts:
                verb = parts[0]
                method = self.lookup_handler(verb) or self.do_UNKNOWN
                await method()

    async def close(self):
        if self._writer:
            self._writer.close()
        self._connection_closed = True

    def lookup_handler(self, verb):
        cmd = "do_{}".format(verb.upper())
        return getattr(self, cmd, None)

    async def push(self, code, msg):
        response = "{} {}\r\n".format(code, msg).encode('utf-8')
        self._writer.write(response)
        await self._writer.drain()

    async def greet(self):
        await self.push(220, '{} ESMTP'.format(self.fqdn))

    async def do_HELO(self):
        await self.push(250, 'OK')

    async def do_EHLO(self):
        response = "250-{}\r\n".format(self.fqdn).encode('utf-8')
        self._writer.write(response)
        responses = ('250-SIZE 512000', '250-VRFY',
                     '250-ENHANCEDSTATUSCODES', '250-8BITMIME', '250 DSN', )
        for response in responses:
            response = "{}\r\n".format(response).encode('utf-8')
            self._writer.write(response)
        await self._writer.drain()

    async def do_MAIL(self):
        await self.push(250, '2.1.0 OK')

    async def do_RCPT(self):
        await self.push(250, '2.1.5 OK')

    async def do_DATA(self):
        await self.push(354, 'End data with <CR><LF>.<CR><LF>')
        while not self.connection_closed:
            line = await self._reader.readline()
            if line == b'.\r\n':
                break
        await self.push(250, '2.0.0 OK: queued as {}'.format(self.message_id))

    async def do_STARTTLS(self):
        await self.do_UNKNOWN()

    async def do_NOOP(self):
        await self.push(250, '2.0.0 OK')

    async def do_RSET(self):
        self.message_id = message_id()
        await self.push(250, '2.0.0 OK')

    async def do_VRFY(self):
        await self.push(252, '2.0.0 OK')

    async def do_QUIT(self):
        await self.push(221, '2.0.0 Goodbye')
        self._handler_coroutine.cancel()
        await self.close()

    async def do_UNKNOWN(self):
        await self.push(500, 'Not implemented')
