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
            headers.append((key.strip(), value.strip()))
        return collections.OrderedDict(headers), text


class Response:

    banner = 'Blackhole HTTP/{}'.format(get_version())
    request = None
    headers = {}
    close = True
    text = ''
    url = ''
    response_type = 'text/html'
    encoding = 'utf-8'
    ok = True
    version = '1.1'
    code = 200
    reason = 'OK'

    def __init__(self, request):
        self.request = request
        self.url = self.request.url
        self.version = self.request.version
        self.headers = self.setup_headers()

    def setup_headers(self):
        headers = [('server', self.banner),
                   ('date', self.date),
                   ('content-length', len(self.text.encode(self.encoding))),
                   ('content-type', self.response_type),
                   ('connection', 'close')]
        return collections.OrderedDict(headers)

    @property
    def date(self):
        now = datetime.datetime.now()
        stamp = time.mktime(now.timetuple())
        return format_date_time(stamp)


class BadRequest(Response):
    ok = False
    code = 400
    reason = 'Bad Request'
    text = 'Invalid HTTP request. Denied.'


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
        verbs_with_body = ('PUT', 'POST')
        crlf_count = 0
        verb = None
        while not self.connection_closed:
            try:
                data = await asyncio.wait_for(self._reader.readline(),
                                              self.config.timeout,
                                              loop=self.loop)
                logger.debug('RECV: %s', data)
                received_data += data.decode('utf-8')
                if verb is None:
                    logger.debug('Verb is None which means this is the first '
                                 'line of data.')
                    verb = self.verb_from_line(data.decode('utf-8'))
                    logger.debug('Got VERB: %s', verb)
                if data == b'\r\n':
                    crlf_count += 1
                if verb is not None and crlf_count >= 1:
                    logger.debug('CRLF count is greater than or equal to 1.')
                    if verb not in verbs_with_body:
                        logger.debug('%s does not provide a body. Break.',
                                     verb)
                        break
                    if verb in verbs_with_body and crlf_count >= 2:
                        logger.debug('%s provides a body and CRLF count is '
                                     'greater than or equal to 2.', verb)
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
        print(resp)
        for key, value in self.response.headers.items():
            resp.append('{}: {}'.format(key.title(), value))
        resp.append('')
        if len(self.response.text) > 0:
            resp.append(self.response.text)
            resp.append('')
        await self.push('\r\n'.join(resp).encode(self.response.encoding))
        await self.close()

    async def process_request(self):
        self.response = BadRequest(self.request)
        print(self.response)
        await self.send_response()

    def verb_from_line(self, line):
        verb, uri, http_ver = line.split(' ')
        return verb

    async def verb(self):
        verb_line = self.headers[0]
        verb = self.verb_from_line(verb_line)
        if verb not in self.verbs:
            await self.bad_request()

    async def bad_request(self):
        logger.debug('Sending Bad Request')
        status = 'HTTP/1.1 400 Bad Request'
        self._response_body = ('Kura', )
        await self.response(status, self.header_generic)

    async def verb_GET(self):
        status = 'HTTP/1.1 200 OK'
        self._response_body = ('Kura', )
        headers = (self.header_server, self.header_content_type,
                   self.header_content_length)
        await self.response(status, headers)
