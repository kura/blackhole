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

"""Provides functionality to spawn and control child processes."""


import collections
import datetime
import time
from wsgiref.handlers import format_date_time

from .status import error
from ..utils import get_version


__all__ = ('Response', 'BadRequest', 'NotFound', 'RequestTimeout',
           'HttpVersionNotSupported')


class Response:

    banner = 'HTTP/{}'.format(get_version())
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
        if self.request.version not in (1.0, 1.1):
            return 1.1
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
            resp = error(self.code)
            self.reason = resp.reason
            return resp.html
        return self._text

    @text.setter
    def text(self, text):
        self._text = text


class BadRequest(Response):
    ok = False
    code = 400


class NotFound(Response):
    ok = False
    code = 404


class RequestTimeout(Response):
    ok = False
    code = 408


class HttpVersionNotSupported(Response):
    ok = False
    code = 505
