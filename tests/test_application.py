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
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys
import unittest

from deiman import Deiman
from mock import patch
from tornado import ioloop
from tornado.options import options

from blackhole.application import (set_action, set_options, fork, daemon)
from blackhole import opts


class TestSetActionStart(unittest.TestCase):

    def setUp(self):
        sys.argv = ['blackhole_unused', 'start']

    def test_set_action_start(self):
        self.assertEquals(set_action(), 'start')


class TestSetActionStop(unittest.TestCase):

    def setUp(self):
        sys.argv = ['blackhole_unused', 'stop']

    def test_set_action_stop(self):
        self.assertEquals(set_action(), 'stop')


class TestSetActionStatus(unittest.TestCase):

    def setUp(self):
        sys.argv = ['blackhole_unused', 'status']

    def test_set_action_status(self):
        self.assertEquals(set_action(), 'status')


class TestSetOptions(unittest.TestCase):

    def setUp(self):
        options.delay = 0
        options.debug = False
        options.ssl = False

    def test_set_options(self):
        set_options()
        self.assertEquals(True, True)


class TestSetOptionsSSLNoCertNoKey(unittest.TestCase):

    def setUp(self):
        options.delay = 0
        options.debug = False
        options.ssl = True
        options.ssl_cert = None
        options.ssl_key = None

    @patch('sys.exit')
    def test_set_options_ssl_no_cert_no_key(self, exit_mock):
        set_options()
        self.assertTrue(exit_mock.called)


class TestSetOptionsSSLCertNoKey(unittest.TestCase):

    def setUp(self):
        options.delay = 0
        options.debug = False
        options.ssl = True
        options.ssl_cert = os.path.join(os.path.dirname(__file__),
                                        "test.crt")
        options.ssl_key = None

    @patch('sys.exit')
    def test_set_options_ssl_cert_no_key(self, exit_mock):
        set_options()
        self.assertTrue(exit_mock.called)


class TestSetOptionsSSLKeyNoCert(unittest.TestCase):

    def setUp(self):
        options.delay = 0
        options.debug = False
        options.ssl = True
        options.ssl_cert = None
        options.ssl_key = os.path.join(os.path.dirname(__file__),
                                       "test.key")

    @patch('sys.exit')
    def test_set_options_ssl_key_no_cert(self, exit_mock):
        set_options()
        self.assertTrue(exit_mock.called)


class TestSetOptionsSSLCertAndKey(unittest.TestCase):

    def setUp(self):
        options.delay = 0
        options.debug = False
        options.ssl = True
        options.ssl_cert = os.path.join(os.path.dirname(__file__),
                                        "test.crt")
        options.ssl_key = os.path.join(os.path.dirname(__file__),
                                       "test.key")

    @patch('sys.exit')
    def test_set_options_ssl_cert_and_key(self, exit_mock):
        set_options()
        self.assertFalse(exit_mock.called)


class TestSetOptionsDebug(unittest.TestCase):

    def setUp(self):
        options.delay = 0
        options.debug = True
        options.ssl = False

    @patch('sys.stdout', new_callable=StringIO)
    def test_set_options_debug(self, stdout_mock):
        val = """WARNING: Using the debug flag!\nThis will generate a lots"""\
              """ of disk I/O and large log files\n\n"""
        set_options()
        self.assertEquals(stdout_mock.getvalue(), val)


class TestSetOptionsDelay(unittest.TestCase):

    def setUp(self):
        options.debug = False
        options.delay = 1
        options.ssl = False

    @patch('sys.stdout', new_callable=StringIO)
    def test_set_options_delay(self, stdout_mock):
        val = """WARNING: Using the delay flag!\n"""\
              """The delay flag is a blocking action """\
              """and will cause connections to block.\n\n"""
        set_options()
        self.assertEquals(stdout_mock.getvalue(), val)


class TestDaemonStop(unittest.TestCase):

    def setUp(self):
        sys.argv = ('blackhole', 'stop')

    @patch('sys.exit')
    @patch('deiman.Deiman.stop')
    def test_daemon_stop(self, exit_mock, daemon_mock):
            daemon('stop')
            self.assertTrue(daemon_mock.called)
            self.assertTrue(exit_mock.called)


class TestDaemonStatus(unittest.TestCase):

    def setUp(self):
        sys.argv = ('blackhole', 'status')

    @patch('sys.exit')
    @patch('deiman.Deiman.status')
    def test_daemon_status(self, exit_mock, daemon_mock):
            daemon('status')
            self.assertTrue(daemon_mock.called)
            self.assertTrue(exit_mock.called)


class TestDaemonStart(unittest.TestCase):

    def setUp(self):
        sys.argv = ('blackhole', 'start')

    @patch('deiman.Deiman.start')
    def test_daemon_start(self, daemon_mock):
            d = daemon('start')
            self.assertTrue(daemon_mock.called)
            self.assertTrue(isinstance(d, Deiman))


class TestDaemonInvalidAction(unittest.TestCase):

    @patch('sys.exit')
    def test_daemon_invalid_action(self, exit_mock):
            daemon('kurakurakura')
            self.assertTrue(exit_mock.called)


class TestFork(unittest.TestCase):

    @patch('blackhole.utils.set_process_title')
    @patch('tornado.process.fork_processes')
    def test_fork(self, set_proc_title_mock, fork_processes_mock):
        io_loop = fork()
        self.assertTrue(set_proc_title_mock.called)
        self.assertTrue(isinstance(io_loop, ioloop.IOLoop))
