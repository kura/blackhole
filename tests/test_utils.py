from io import StringIO
import re
from unittest import mock

from blackhole.utils import message_id, mailname


@mock.patch('os.getpid', return_value='1234')
@mock.patch('random.randrange', return_value='1234567890')
def test_message_id_generator(mock_pid, mock_range):
    # 20160417114222.30668.1969251287.0@kura>
    r = r"\<[0-9]{14}\.[0-9]{4}\.[0-9]{10}\.[0-9]{1,3}\@[a-z0-9\-_\.]*\>"
    mid = re.compile(r, re.IGNORECASE)
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
