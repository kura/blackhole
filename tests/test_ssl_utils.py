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

from tornado.options import options

from blackhole import opts
from blackhole.ssl_utils import (BlackholeSSLException, verify_ssl_opts)


class TestNoSSLKey(unittest.TestCase):

    def setUp(self):
        options.ssl_key = None

    def test_no_ssl_key(self):
        self.assertRaises(BlackholeSSLException, verify_ssl_opts)


class TestNoSSLCert(unittest.TestCase):

    def setUp(self):
        options.ssl_cert = None

    def test_no_ssl_cert(self):
        self.assertRaises(BlackholeSSLException, verify_ssl_opts)


class TestSSLKeyNoCert(unittest.TestCase):

    def setUp(self):
        options.ssl_cert = None
        options.ssl_key = os.path.join(os.path.dirname(__file__),
                                       "test.key")

    def test_ssl_key_no_cert(self):
        self.assertRaises(BlackholeSSLException, verify_ssl_opts)


class TestSSLCertNoKey(unittest.TestCase):

    def setUp(self):
        options.ssl_cert = os.path.join(os.path.dirname(__file__),
                                        "test.crt")
        options.ssl_key = None

    def test_ssl_cert_no_key(self):
        self.assertRaises(BlackholeSSLException, verify_ssl_opts)


class TestSSLCertAndKey(unittest.TestCase):

    def setUp(self):
        options.ssl_cert = os.path.join(os.path.dirname(__file__),
                                        "test.crt")
        options.ssl_key = os.path.join(os.path.dirname(__file__),
                                       "test.key")

    def test_ssl_cert_no_key(self):
        self.assertEquals(verify_ssl_opts(), True)
