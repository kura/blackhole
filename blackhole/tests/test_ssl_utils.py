import os
import unittest

from tornado.options import options

from blackhole.opts import *
from blackhole.ssl_utils import BlackholeSSLException,\
    verify_ssl_opts


class TestNoSSLKey(unittest.TestCase):

    def setUp(self):
        options.ssl_key = None

    def test_no_ssl_key(self):
        with self.assertRaises(BlackholeSSLException):
            verify_ssl_opts()


class TestNoSSLCert(unittest.TestCase):

    def setUp(self):
        options.ssl_cert = None

    def test_no_ssl_cert(self):
        with self.assertRaises(BlackholeSSLException):
            verify_ssl_opts()


class TestSSLKeyNoCert(unittest.TestCase):

    def setUp(self):
        options.ssl_cert = None
        options.ssl_key = os.path.join(os.path.dirname(__file__),
                                       "test.key")

    def test_ssl_key_no_cert(self):
        with self.assertRaises(BlackholeSSLException):
            verify_ssl_opts()


class TestSSLCertNoKey(unittest.TestCase):

    def setUp(self):
        options.ssl_cert = os.path.join(os.path.dirname(__file__),
                                       "test.crt")
        options.ssl_key = None

    def test_ssl_cert_no_key(self):
        with self.assertRaises(BlackholeSSLException):
            verify_ssl_opts()


class TestSSLCertAndKey(unittest.TestCase):

    def setUp(self):
        options.ssl_cert = os.path.join(os.path.dirname(__file__),
                                       "test.crt")
        options.ssl_key = os.path.join(os.path.dirname(__file__),
                                       "test.key")

    def test_ssl_cert_no_key(self):
        self.assertEquals(verify_ssl_opts(), True)
