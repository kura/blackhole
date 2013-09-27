# (The MIT License)
#
# Copyright (c) 2013 Kura
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

import os
import unittest
import random
import socket

from tornado.options import options
from tornado import iostream

from blackhole.connection import connection_stream
from blackhole import opts
from blackhole.ssl_utils import sslkwargs


class BaseStream(unittest.TestCase):

    def setUp(self):
        options.ssl = False
        options.port = random.randint(5000, 10000)
        options.ssl_port = random.randint(5000, 10000)

    def tearDown(self):
        for s in self.sockets.values():
            s.close()
        self.sockets = {}


class TestSocketConnectionStream(BaseStream):

    def setUp(self):
        super(TestSocketConnectionStream, self).setUp()
        self.socket = socket.socket()

    def test_socket_connection_stream(self):
        self.assertTrue(isinstance(connection_stream(self.socket),
                                   iostream.IOStream))

    def tearDown(self):
        self.socket.close()


class TestSSLSocketConnectionStream(BaseStream):

    def setUp(self):
        super(TestSSLSocketConnectionStream, self).setUp()
        options.ssl = True
        sslkwargs['keyfile'] = os.path.join(os.path.dirname(__file__),
                                            'test.key')
        sslkwargs['certfile'] = os.path.join(os.path.dirname(__file__),
                                             'test.crt')
        self.socket = socket.socket()
        self.socket.bind(('127.0.0.1', options.ssl_port))

    def test_ssl_socket_connection_stream(self):
        self.assertTrue(isinstance(connection_stream(self.socket),
                        iostream.SSLIOStream))

    def tearDown(self):
        self.socket.close()
