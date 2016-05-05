from io import StringIO
from unittest import mock

from blackhole.utils import mailname


def test_mail_name_file():
    check_value = 'file.blackhole.io'
    with mock.patch('os.path.exists', return_value=True), \
            mock.patch('builtins.open', return_value=StringIO(check_value)):
        mn = mailname()
        assert mn == check_value


def test_mail_name_socket():
    check_value = 'socket.blackhole.io'
    with mock.patch('os.path.exists', return_value=False), \
            mock.patch('socket.getfqdn', return_value='socket.blackhole.io'):
        mn = mailname()
    assert mn == check_value
