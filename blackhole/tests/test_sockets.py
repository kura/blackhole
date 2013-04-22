import unittest
import random
import socket

from tornado.options import options

from blackhole.connection import sockets
from blackhole.opts import *


class TestNoSSLPorts(unittest.TestCase):

    def setUp(self):
        options.ssl = False

    def test_no_ssl_ports(self):
        self.assertEquals(ports(), ['std', ])

class TestSSLPorts(unittest.TestCase):

    def setUp(self):
        options.ssl=True

    def test_no_ssl_ports(self):
        self.assertEquals(ports(), ['std', 'ssl'])


class BaseSocket(unittest.TestCase):

    def setUp(self):
        options.ssl = False
        options.port = random.randint(5000, 10000)
        options.ssl_port = random.randint(5000, 10000)

    def tearDown(self):
        for s in self.sockets.itervalues():
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
