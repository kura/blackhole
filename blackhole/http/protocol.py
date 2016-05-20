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

"""Provides the Http protocol wrapper."""


import asyncio
import logging

from .request import Request
from .response import (Response, NotFound, BadRequest, RequestTimeout,
                       HttpVersionNotSupported)
from ..protocols import Protocol


__all__ = ('Http', )


logger = logging.getLogger('blackhole.http')


class Http(Protocol):

    verbs = ('GET', 'HEAD', 'PUT', 'POST')
    _response_body = []
    _received_data = ''

    def __init__(self, clients, flags, loop=None):
        """
        Initialise the HTTP protocol.

        :param clients: A list of connected clients.
        :type clients: :any:`list`
        :param loop: The event loop to use.
        :type loop: :any:`None` or
                    :any:`syncio.unix_events._UnixSelectorEventLoop`
        """
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        super().__init__(clients, flags, loop=loop)

    async def _handle_client(self):
        while not self.connection_closed:
            await self.wait()

    async def wait(self):
        received_data = b''
        while not self.connection_closed:
            try:
                data = await asyncio.wait_for(self._reader.read(1024),
                                              self.config.timeout,
                                              loop=self.loop)
                if data == b'':
                    return
                logger.debug('RECV: %s', data)
                received_data += data
                if data.endswith(b'\r\n\r\n'):
                    break
                if received_data.endswith(b'\r\n\r\n'):
                    break
            except asyncio.TimeoutError:
                await self.timeout()
        self.request = Request(received_data)
        await self.process_request()

    async def timeout(self):
        logger.debug('Peer timed out, no data received for %d seconds',
                     self.config.timeout)
        self.request = Request()
        self.response = RequestTimeout(self.request)
        await self.send_response()

    async def push(self, msg):
        logger.debug('SEND: %s', msg)
        self._writer.write(msg.encode(self.response.encoding))
        await self._writer.drain()

    async def send_response(self):
        resp = ['HTTP/{} {} {}'.format(str(self.response.version),
                                       self.response.code,
                                       self.response.reason), ]
        for key, value in self.response.headers.items():
            resp.append('{}: {}'.format(key.title(), value))
        resp.append('')
        if len(self.response.text) > 0:
            resp.append(self.response.text)
            resp.append('')
        await self.push('\r\n'.join(resp))
        if self.response.close:
            await self.close()
        await self.wait()

    async def process_request(self):
        if self.request.version not in (1.0, 1.1):
            self.response = HttpVersionNotSupported(self.request)
            await self.send_response()
            return
        if 'host' not in self.request.headers.keys():
            self.response = BadRequest(self.request)
            await self.send_response()
            return
        if self.request.headers.get('host') != self.fqdn:
            self.response = NotFound(self.request)
            await self.send_response()
            return
        self.response = NotFound(self.request)
        await self.send_response()
        return
