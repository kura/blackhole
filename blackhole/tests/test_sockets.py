import unittest2
import random
import socket

from tornado.options import options

from blackhole.connection import sockets
from blackhole.opts import *


class TestSSLSocketIsSet(unittest2.TestCase):

    def setUp(self):
        options.ssl = True
        options.port = random.randint(5000, 10000)
        options.ssl_port = random.randint(5000, 10000)

    def test_ssl_socket_is_set(self):
        self.assertIsInstance(sockets()['ssl'], socket.socket)


class TestSSLSocketIsNotSet(unittest2.TestCase):

    def setUp(self):
        options.port = random.randint(5000, 10000)
        options.ssl_port = random.randint(5000, 10000)
        options.ssl = False

    def test_ssl_socket_is_set(self):
        self.assertNotIn('ssl', sockets())
