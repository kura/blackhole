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

import re
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import unittest

from mock import patch

from blackhole import opts
from blackhole.utils import (email_id, get_mailname, setgid, setuid)


class TestEmailIDGenerator(unittest.TestCase):

    def test_email_id_generator(self):
        self.assertTrue(re.match(r"^[A-F0-9]{10}$", email_id()))


class TestMailNameFile(unittest.TestCase):
    check_value = "file.blackhole.io"

    @patch('os.path.exists', return_value=True)
    def test_mail_name_file(self, exists_mock):
        try:
            with patch('__builtin__.open',
                       return_value=StringIO(self.check_value)):
                mn = get_mailname()
                self.assertEqual(mn, self.check_value)
        except ImportError:
            with patch('builtins.open',
                       return_value=StringIO(self.check_value)):
                mn = get_mailname()
                self.assertEqual(mn, self.check_value)


class TestMailNameSocket(unittest.TestCase):
    check_value = "socket.blackhole.io"

    @patch('os.path.exists', return_value=False)
    @patch('socket.getfqdn', return_value=check_value)
    def test_mail_name_socket(self, exists_mock, socket_mock):
        mn = get_mailname()
        self.assertEqual(mn, self.check_value)


class TestChgGroupNoGroup(unittest.TestCase):

    @patch('os.setgid', return_value=KeyError)
    @patch('grp.getgrnam')
    @patch('sys.exit')
    def test_change_group_no_group(self, setgid_mock, getgrname_mock,
                                   exit_mock):
        setgid()
        self.assertTrue(exit_mock.called)


class TestChgGroupNoPermission(unittest.TestCase):

    @patch('os.setgid', return_value=OSError)
    @patch('grp.getgrnam')
    @patch('sys.exit')
    def test_change_group_no_permission(self, setgid_mock, getgrname_mock,
                                        exit_mock):
        setgid()
        self.assertTrue(exit_mock.called)


class TestChgGroupValid(unittest.TestCase):

    @patch('os.setgid', return_value=True)
    @patch('grp.getgrnam')
    def test_change_group_valid(self, setgid_mock, getgrname_mock):
        with patch('sys.exit') as exit_mock:
            setgid()
            self.assertFalse(exit_mock.called)


class TestChgUserNoUser(unittest.TestCase):

    @patch('os.setuid', return_value=KeyError)
    @patch('pwd.getpwnam')
    @patch('sys.exit')
    def test_change_user_no_user(self, setgid_mock, getpwnam_mock,
                                 exit_mock):
        setuid()
        self.assertTrue(exit_mock.called)


class TestChgUserNoPermission(unittest.TestCase):

    @patch('os.setuid', return_value=OSError)
    @patch('pwd.getpwnam')
    @patch('sys.exit')
    def test_change_user_no_permission(self, setgid_mock, getpwnam_mock,
                                       exit_mock):
        setuid()
        self.assertTrue(exit_mock.called)


class TestChgUserValid(unittest.TestCase):

    @patch('os.setuid', return_value=True)
    @patch('pwd.getpwnam')
    def test_change_user_valid(self, setgid_mock, getpwnam_mock):
        with patch('sys.exit') as exit_mock:
            setuid()
            self.assertFalse(exit_mock.called)
