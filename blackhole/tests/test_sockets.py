import unittest2
import random
import socket

from tornado.options import options

from blackhole.connection import sockets
from blackhole.opts import *


class BaseSocketTest(unittest2.TestCase):

    def setUp(self):
        options.ssl = True
        options.port = random.randint(5000, 10000)
        options.ssl_port = random.randint(5000, 10000)

    def tearDown(self):
        for s in self.sockets.itervalues():
            s.close()
        self.sockets = {}


class TestSSLSocketIsSet(BaseSocketTest):

    def setUp(self):
        super(TestSSLSocketIsSet, self).setUp()
        self.sockets = sockets()

    def test_ssl_socket_is_set(self):
        self.assertIsInstance(self.sockets['ssl'], socket.socket)

class TestSSLSocketIsNotSet(BaseSocketTest):

    def setUp(self):
        super(TestSSLSocketIsNotSet, self).setUp()
        options.ssl = False
        self.sockets = sockets()

    def test_ssl_socket_is_not_set(self):
        self.assertNotIn('ssl', self.sockets)
