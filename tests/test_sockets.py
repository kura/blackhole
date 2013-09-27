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

import unittest
import random
import socket

from tornado.options import options

from blackhole.connection import sockets
from blackhole import opts


class TestNoSSLPorts(unittest.TestCase):

    def setUp(self):
        options.ssl = False

    def test_no_ssl_ports(self):
        self.assertEquals(opts.ports(), ['std', ])


class TestSSLPorts(unittest.TestCase):

    def setUp(self):
        options.ssl = True

    def test_no_ssl_ports(self):
        self.assertEquals(opts.ports(), ['std', 'ssl'])


class BaseSocket(unittest.TestCase):

    def setUp(self):
        options.ssl = False
        options.port = random.randint(5000, 10000)
        options.ssl_port = random.randint(5000, 10000)

    def tearDown(self):
        for s in self.sockets.values():
            s.close()
        self.sockets = {}


class TestSocketIsSet(BaseSocket):

    def setUp(self):
        super(TestSocketIsSet, self).setUp()
        self.ssl = False
        self.sockets = sockets()

    def test_ssl_socket_is_set(self):
        self.assertTrue(isinstance(self.sockets['std'], socket.socket))


class TestSSLSocketIsSet(BaseSocket):

    def setUp(self):
        super(TestSSLSocketIsSet, self).setUp()
        options.ssl = True
        self.sockets = sockets()

    def test_ssl_socket_is_set(self):
        self.assertTrue(isinstance(self.sockets['ssl'], socket.socket))


class TestSSLSocketIsNotSet(BaseSocket):

    def setUp(self):
        super(TestSSLSocketIsNotSet, self).setUp()
        options.ssl = False
        self.sockets = sockets()

    def test_ssl_socket_is_not_set(self):
        self.assertTrue('ssl' not in self.sockets)
