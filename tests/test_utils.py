# (The MIT License)
#
# Copyright (c) 2013-2017 Kura
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

# pylama:skip=1

from io import StringIO
from unittest import mock

import pytest

from blackhole.utils import get_version, mailname, message_id

from ._utils import (Args, cleandir, create_config, create_file, reset)


@pytest.mark.usefixtures('reset', 'cleandir')
def test_mail_name_file():
    check_value = 'file.blackhole.io'
    with mock.patch('os.access', return_value=True), \
            mock.patch('codecs.open', return_value=StringIO(check_value)):
        mn = mailname()
        assert mn == check_value


@pytest.mark.usefixtures('reset', 'cleandir')
def test_mail_name_socket():
    check_value = 'socket.blackhole.io'
    with mock.patch('os.access', return_value=False), \
            mock.patch('socket.getfqdn', return_value='socket.blackhole.io'):
        mn = mailname()
    assert mn == check_value


@pytest.mark.usefixtures('reset', 'cleandir')
def test_mail_name_file_length_0():
    mnfile = create_file('mailname')
    check_value = 'socket.blackhole.io'
    with mock.patch('os.access', return_value=True), \
            mock.patch('socket.getfqdn', return_value='socket.blackhole.io'):
        mn = mailname(mnfile)
    assert mn == check_value


@pytest.mark.usefixtures('reset', 'cleandir')
def test_mail_name_file_garbage():
    mnfile = create_file('mailname', '            \n     ')
    check_value = 'socket.blackhole.io'
    with mock.patch('os.access', return_value=True), \
            mock.patch('socket.getfqdn', return_value='socket.blackhole.io'):
        mn = mailname(mnfile)
    assert mn == check_value


@pytest.mark.usefixtures('reset', 'cleandir')
def test_message_id():
    with mock.patch('time.monotonic',
                    return_value=1463290829.4173775) as mock_time, \
        mock.patch('os.getpid', return_value=9000) as mock_getpid, \
            mock.patch('random.getrandbits',
                       return_value=17264867586200823825) as mock_randbits:
        ex_mid = '<{}.{}.{}@blackhole.io>'.format(int(1463290829.4173775 *
                                                  100),
                                                  9000, 17264867586200823825)
        assert message_id('blackhole.io') == ex_mid
    assert mock_time.called is True
    assert mock_getpid.called is True
    assert mock_randbits.called is True


@pytest.mark.usefixtures('reset', 'cleandir')
def test_get_version():
    version_file = create_file('version.py', '__version__ = "9.9.9"')
    with mock.patch('os.path.join', return_value=version_file):
        assert get_version() == '9.9.9'


@pytest.mark.usefixtures('reset', 'cleandir')
def test_get_version_no_access():
    with mock.patch('os.access', return_value=False), \
            pytest.raises(OSError) as err:
        get_version()
    assert str(err.value) == 'Cannot open __init__.py file for reading'


@pytest.mark.usefixtures('reset', 'cleandir')
def test_get_version_invalid_version_split():
    version_file = create_file('version.py', '__version__')
    with mock.patch('os.path.join', return_value=version_file), \
            pytest.raises(AssertionError) as err:
        get_version()
    assert str(err.value) == 'Cannot extract version from __version__'


@pytest.mark.usefixtures('reset', 'cleandir')
def test_get_version_invalid_version():
    version_file_a = create_file('versiona.py', '__version__ = a.1')
    with mock.patch('os.path.join', return_value=version_file_a), \
            pytest.raises(AssertionError) as err:
        get_version()
    assert str(err.value) == 'a.1 is not a valid version number'
    version_file_b = create_file('versionb.py', '__version__ = a.1.1')
    with mock.patch('os.path.join', return_value=version_file_b), \
            pytest.raises(AssertionError) as err:
        get_version()
    assert str(err.value) == 'a.1.1 is not a valid version number'
    version_file_c = create_file('versionc.py', '__version__ = 1.a.1')
    with mock.patch('os.path.join', return_value=version_file_c), \
            pytest.raises(AssertionError) as err:
        get_version()
    assert str(err.value) == '1.a.1 is not a valid version number'
    version_file_d = create_file('versiond.py', '__version__ = 1.1.a')
    with mock.patch('os.path.join', return_value=version_file_d), \
            pytest.raises(AssertionError) as err:
        get_version()
    assert str(err.value) == '1.1.a is not a valid version number'


@pytest.mark.usefixtures('reset', 'cleandir')
def test_get_version_version_not_found():
    version_file = create_file('version.py', 'version = "abc"')
    with mock.patch('os.path.join', return_value=version_file), \
            pytest.raises(AssertionError) as err:
        get_version()
    assert str(err.value) == 'No __version__ assignment found'
