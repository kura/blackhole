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

"""Provides the Smtp protocol wrapper."""


import asyncio
import collections
import datetime
import logging
import time
from wsgiref.handlers import format_date_time

from .config import Config
from .utils import get_version


__all__ = ('Http', )


logger = logging.getLogger('blackhole.http')


errors = {400: '''    44    00000   00000
   444   00   00 00   00
 44  4   00   00 00   00
44444444 00   00 00   00
   444    00000   00000

001101000011000000110000''',
404: '''    44    00000      44
   444   00   00    444
 44  4   00   00  44  4
44444444 00   00 44444444
   444    00000     444

001101000011000000110100''',
403: '''    44    00000  333333
   444   00   00    3333
 44  4   00   00   3333
44444444 00   00     333
   444    00000  333333

00110100 00110000 00110011''',
405: '''    44    00000  555555
   444   00   00 55
 44  4   00   00 555555
44444444 00   00    5555
   444    00000  555555

00110100 00110000 00110101''',
408: '''    44    00000   88888
   444   00   00 88   88
 44  4   00   00  88888
44444444 00   00 88   88
   444    00000   88888

00110100 00110000 00111000''',
413: '''    44    1  333333
   444   111    3333
 44  4    11   3333
44444444  11     333
   444   111 333333

00110100 00110001 00110011''',
500: '''555555   00000   00000
55      00   00 00   00
555555  00   00 00   00
   5555 00   00 00   00
555555   00000   00000

00110101 00110000 00110000''',
503: '''555555   00000  333333
55      00   00    3333
555555  00   00   3333
   5555 00   00     333
555555   00000  333333

00110101 00110000 00110011''',
505: '''555555   00000  555555
55      00   00 55
555555  00   00 555555
   5555 00   00    5555
555555   00000  555555

00110101 00110000 00110101'''}


class Request:

    fqdn = 'blackhole.io'
    raw = ''
    method = 'GET'
    path_url = ''
    version = '1.1'
    url = ''
    headers = {}
    text = ''

    def __init__(self, raw_request):
        self.config = Config()
        self.fqdn = self.config.mailname
        self.setup(raw_request)

    def setup(self, raw_request):
        self.raw = raw_request
        self.method, self.path_url, self.version = self.parse_baseline()
        self.url = self.fqdn + self.path_url
        self.headers, self.text = self.parse_request()

    def parse_baseline(self):
        baseline = self.raw.split('\r\n', 1)[0]
        meth, path, over = baseline.split(' ')
        ver = over.split('/', 1)[1]
        return meth, path, ver

    def parse_request(self):
        oheaders, text = self.raw.split('\r\n\r\n', 1)
        headers = []
        for header in oheaders.split('\r\n')[1:]:
            key, value = header.split(':', 1)
            headers.append((key.strip().lower(), value.strip().lower()))
        return collections.OrderedDict(headers), text

    @property
    def close(self):
        if 'connection' in self.headers.keys():
            conn = self.headers.get('connection')
            if conn == 'close':
                return True
            if conn == 'keep-alive':
                return False
        return True


class Response:

    banner = 'Blackhole HTTP/{}'.format(get_version())
    request = None
    headers = {}
    _text = ''
    content_type = 'text/html'
    encoding = 'utf-8'
    ok = True
    code = 200
    reason = 'OK'

    def __init__(self, request):
        self.request = request
        self.headers = self.setup_headers()

    def setup_headers(self):
        headers = [('server', self.banner),
                   ('date', self.date),
                   ('content-length', self.content_length),
                   ('content-type', self.content_type),
                   ('connection', self.connection)]
        return collections.OrderedDict(headers)

    @property
    def version(self):
        return self.request.version

    @property
    def url(self):
        return self.request.url

    @property
    def connection(self):
        if self.close is True:
            return 'close'
        else:
            return 'keep-alive'

    @property
    def close(self):
        return self.request.close

    @property
    def date(self):
        now = datetime.datetime.now()
        stamp = time.mktime(now.timetuple())
        return format_date_time(stamp)

    @property
    def content_length(self):
        return len(self.text.encode(self.encoding))

    @property
    def text(self):
        if self.ok is False:
            art = errors[self.code]
            return ('<html><head><title>{}</title></head>'
                    '<body><center><pre>{}</pre></center></body>'
                    '</html>'.format(self.code, art))
        return self._text

    @text.setter
    def text(self, text):
        self._text = text


class BadRequest(Response):
    ok = False
    code = 400
    reason = 'Bad Request'


class NotFound(Response):
    ok = False
    code = 404
    reason = 'Not Found'


class Http(asyncio.StreamReaderProtocol):

    verbs = ('GET', 'HEAD', 'PUT', 'POST')
    _response_body = []
    _received_data = ''
    flags = {}

    def __init__(self, clients, flags, loop=None):
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        super().__init__(asyncio.StreamReader(loop=self.loop),
                         client_connected_cb=self._client_connected_cb,
                         loop=self.loop)
        self.clients = clients
        self.config = Config()
        self.flags = flags
        self.fqdn = self.config.mailname

    def connection_made(self, transport):
        """
        Tie a connection to blackhole to the SMTP protocol.

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

    async def _handle_client(self):
        while not self.connection_closed:
            await self.wait()

    async def wait(self):
        received_data = ''
        while not self.connection_closed:
            try:
                data = await asyncio.wait_for(self._reader.read(1024),
                                              self.config.timeout,
                                              loop=self.loop)
                if data == b'':
                    return
                logger.debug('RECV: %s', data)
                received_data += data.decode('utf-8')
                if data.endswith(b'\r\n\r\n'):
                    break
                if received_data.endswith('\r\n\r\n'):
                    break
            except asyncio.TimeoutError:
                await self.timeout()
        self.request = Request(received_data)
        await self.process_request()

    async def timeout(self):
        logger.debug('Peer timed out, no data received for %d seconds',
                     self.config.timeout)
        await self.close()

    async def close(self):
        logger.debug('Closing connection')
        if self._writer:
            try:
                self.clients.remove(self._writer)
            except ValueError:
                pass
            self._writer.close()
            await self._writer.drain()
        self._connection_closed = True

    async def push(self, msg):
        logger.debug('SEND: %s', msg)
        self._writer.write(msg)
        await self._writer.drain()

    async def send_response(self):
        resp = ['HTTP/{} {} {}'.format(self.response.version,
                                       self.response.code,
                                       self.response.reason), ]
        for key, value in self.response.headers.items():
            resp.append('{}: {}'.format(key.title(), value))
        resp.append('')
        if len(self.response.text) > 0:
            resp.append(self.response.text)
            resp.append('')
        await self.push('\r\n'.join(resp).encode(self.response.encoding))
        if self.response.close:
            await self.close()
        await self.wait()

    async def process_request(self):
        self.response = NotFound(self.request)
        await self.send_response()
