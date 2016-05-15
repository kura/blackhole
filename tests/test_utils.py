from io import StringIO
from unittest import mock

from blackhole.utils import mailname

from ._utils import *


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_mail_name_file():
    check_value = 'file.blackhole.io'
    with mock.patch('os.access', return_value=True), \
            mock.patch('builtins.open', return_value=StringIO(check_value)):
        mn = mailname()
        assert mn == check_value


@pytest.mark.usefixtures('reset_conf', 'reset_daemon', 'reset_supervisor',
                         'cleandir')
def test_mail_name_socket():
    check_value = 'socket.blackhole.io'
    with mock.patch('os.access', return_value=False), \
            mock.patch('socket.getfqdn', return_value='socket.blackhole.io'):
        mn = mailname()
    assert mn == check_value
