from io import StringIO
import re
from unittest import mock

from blackhole.utils import mailname


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
