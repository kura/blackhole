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

from io import StringIO
import re
from unittest import mock

from blackhole.utils import (message_id, mailname)


@mock.patch('os.getpid', return_value='1234')
@mock.patch('random.randrange', return_value='1234567890')
def test_message_id_generator(mock_pid, mock_range):
    # 20160417114222.30668.1969251287.0@kura>
    r = r"\<[0-9]{14}\.[0-9]{4}\.[0-9]{10}\.[0-9]{1,3}\@[a-z0-9\-_\.]*\>"
    mid = re.compile(r, re.IGNORECASE)
    print(message_id())
    assert mid.match(message_id()) is not None


@mock.patch('os.path.exists', return_value=True)
def test_mail_name_file(mock_os):
    check_value = 'file.blackhole.io'
    with mock.patch('builtins.open',
                    return_value=StringIO(check_value)):
        mn = mailname()
        assert mn == check_value


@mock.patch('os.path.exists', return_value=False)
@mock.patch('socket.getfqdn', return_value='socket.blackhole.io')
def test_mail_name_socket(mock_os, mock_socket):
    check_value = 'socket.blackhole.io'
    mn = mailname()
    assert mn == check_value
