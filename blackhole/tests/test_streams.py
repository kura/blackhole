import os
import unittest
import random
import socket

from tornado.options import options
from tornado import iostream

from blackhole.connection import connection_stream
from blackhole.opts import *
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
        self.assertIsInstance(connection_stream(self.socket), iostream.IOStream)

    def tearDown(self):
        self.socket.close()


class TestSSLSocketConnectionStream(BaseStream):

    def setUp(self):
        super(TestSSLSocketConnectionStream, self).setUp()
        options.ssl = True
        self.socket = socket.socket()
        self.socket.bind(('127.0.0.1', options.ssl_port))
        sslkwargs['keyfile'] = os.path.join(os.path.dirname(__file__), 'test.key')
        sslkwargs['certfile'] = os.path.join(os.path.dirname(__file__), 'test.crt')

    def test_ssl_socket_connection_stream(self):
        self.assertIsInstance(connection_stream(self.socket), iostream.SSLIOStream)

    def tearDown(self):
        self.socket.close()
