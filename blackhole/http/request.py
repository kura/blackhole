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

from ..config import Config


__all__ = ('Request', )


class Request:

    fqdn = 'blackhole.io'
    raw = ''
    method = 'GET'
    path_url = ''
    version = 1.1
    url = ''
    headers = {}
    text = ''

    def __init__(self, raw_request=None):
        self.config = Config()
        self.fqdn = self.config.mailname
        if raw_request is None:
            return
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
        return meth, path, float(ver)

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
