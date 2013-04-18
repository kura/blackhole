import unittest2
import random
import socket

from tornado.options import options
from tornado import iostream

from blackhole.connection import connection_stream
from blackhole.opts import *


class BaseStream(unittest2.TestCase):

    def setUp(self):
        options.ssl = False
        options.port = random.randint(5000, 10000)
        options.ssl_port = random.randint(5000, 10000)

    def tearDown(self):
        for s in self.sockets.itervalues():
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

    def test_ssl_socket_connection_stream(self):
        self.assertIsInstance(connection_stream(self.socket), iostream.SSLIOStream)

    def tearDown(self):
        self.socket.close()