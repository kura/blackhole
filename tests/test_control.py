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

import os
import socket
import unittest
from unittest import mock

import pytest

from blackhole.config import Config
from blackhole.control import (_context, _socket, pid_permissions, server,
                               setgid, setuid)
from blackhole.exceptions import BlackholeRuntimeException

from ._utils import (Args, cleandir, create_config, create_file, reset)

try:
    import ssl
except ImportError:
    ssl = None


@pytest.mark.usefixtures('reset', 'cleandir')
def test_tls_context_no_config():
    ctx = _context()
    assert ctx is None


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_tls_context_no_dhparams():
    tls_cert = create_file('cert.cert')
    tls_key = create_file('key.key')
    cfile = create_config(('listen=127.0.0.1:25', 'tls_listen=127.0.0.1:9000',
                           'tls_cert={}'.format(tls_cert),
                           'tls_key={}'.format(tls_key), ))
    conf = Config(cfile).load()
    conf.args = Args((('less_secure', False), ))
    with mock.patch('ssl.SSLContext.load_cert_chain'):
        _context(use_tls=True)


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_tls_context_less_secure():
    tls_cert = create_file('cert.cert')
    tls_key = create_file('key.key')
    cfile = create_config(('listen=127.0.0.1:25', 'tls_listen=127.0.0.1:9000',
                           'tls_cert={}'.format(tls_cert),
                           'tls_key={}'.format(tls_key), ))
    conf = Config(cfile).load()
    conf.args = Args((('less_secure', True), ))
    with mock.patch('ssl.SSLContext.load_cert_chain'):
        _context(use_tls=True)


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_tls_context_dhparams():
    tls_cert = create_file('cert.cert')
    tls_key = create_file('key.key')
    tls_dhparams = create_file('dhparams.pem')
    cfile = create_config(('listen=127.0.0.1:25', 'tls_listen=127.0.0.1:9000',
                           'tls_cert={}'.format(tls_cert),
                           'tls_key={}'.format(tls_key),
                           'tls_dhparams={}'.format(tls_dhparams)))
    conf = Config(cfile).load()
    conf.args = Args((('less_secure', False), ))
    with mock.patch('ssl.SSLContext.load_cert_chain'), \
            mock.patch('ssl.SSLContext.load_dh_params') as dh:
        _context(use_tls=True)
    assert dh.called is True


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_create_ipv6_socket_fails():
    with mock.patch('socket.socket.bind', side_effect=OSError), \
            pytest.raises(BlackholeRuntimeException):
        _socket('::', 25, socket.AF_INET)


@pytest.mark.usefixtures('reset', 'cleandir')
def test_create_ipv4_socket_fails():
    with mock.patch('socket.socket.bind', side_effect=OSError), \
            pytest.raises(BlackholeRuntimeException):
        _socket('127.0.0.1', 25, socket.AF_INET)


@pytest.mark.usefixtures('reset', 'cleandir')
def test_create_server_ipv4_bind_fails():
    cfile = create_config(('listen=127.0.0.1:9000', ))
    Config(cfile).load()
    with mock.patch('socket.socket.bind',
                    side_effect=OSError) as mock_sock, \
            pytest.raises(BlackholeRuntimeException):
        server('127.0.0.1', 9000, socket.AF_INET, {})
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_create_server_ipv6_bind_fails():
    cfile = create_config(('listen=:::9000', ))
    Config(cfile).load()
    with mock.patch('socket.socket.bind',
                    side_effect=OSError) as mock_sock, \
            pytest.raises(BlackholeRuntimeException):
        server('::', 9000, socket.AF_INET6, {})
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@pytest.mark.usefixtures('reset', 'cleandir')
@mock.patch('socket.socket.bind')
def test_create_server_ipv4_bind_works(mock_sock):
    cfile = create_config(('listen=127.0.0.1:9000', ))
    Config(cfile).load()
    server('127.0.0.1', 9000, socket.AF_INET, {})
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_create_server_ipv6_bind_works():
    cfile = create_config(('listen=:::9000', ))
    Config(cfile).load()
    with mock.patch('socket.socket.bind') as mock_sock:
        server('::', 9000, socket.AF_INET6, {})
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_create_server_ipv4_tls_bind_fails():
    cfile = create_config(('tls_listen=127.0.0.1:9000', ))
    Config(cfile).load()
    with mock.patch('socket.socket.bind',
                    side_effect=OSError) as mock_sock, \
            pytest.raises(BlackholeRuntimeException):
        server('127.0.0.1', 9000, socket.AF_INET, {})
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_create_server_ipv6_tls_bind_fails():
    cfile = create_config(('tls_listen=:::9000', ))
    Config(cfile).load()
    with mock.patch('socket.socket.bind',
                    side_effect=OSError) as mock_sock, \
            pytest.raises(BlackholeRuntimeException):
        server('::', 9000, socket.AF_INET6, {})
    assert mock_sock.called is True
    assert mock_sock.call_count is 1


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_create_server_tls_ipv4_bind_works():
    cfile = create_config(('listen=127.0.0.1:25',
                           'tls_listen=127.0.0.1:9000', ))
    conf = Config(cfile).load()
    conf.args = Args((('less_secure', False), ))
    with mock.patch('socket.socket.bind') as mock_sock, \
            mock.patch('ssl.create_default_context') as mock_ssl:
        server('127.0.0.1', 9000, socket.AF_INET, {}, use_tls=True)
    assert mock_sock.called is True
    assert mock_sock.call_count is 1
    assert mock_ssl.called is True
    assert mock_ssl.call_count is 1


@unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_create_server_tls_ipv6_bind_works():
    cfile = create_config(('listen=:::25',
                           'tls_listen=:::9000', ))
    conf = Config(cfile).load()
    conf.args = Args((('less_secure', False), ))
    with mock.patch('socket.socket.bind') as mock_sock, \
            mock.patch('ssl.create_default_context') as mock_ssl:
        server('::', 9000, socket.AF_INET6, {}, use_tls=True)
    assert mock_sock.called is True
    assert mock_sock.call_count is 1
    assert mock_ssl.called is True
    assert mock_ssl.call_count is 1


class Grp(mock.MagicMock):
    gr_name = 'testgroup'
    gr_gid = 9000


@pytest.mark.usefixtures('reset', 'cleandir')
def test_setgid():
    cfile = create_config(('group=abc', ))
    with mock.patch('grp.getgrnam') as mock_getgrnam, \
            mock.patch('os.setgid') as mock_setgid:
        Config(cfile).load()
        setgid()
    assert mock_getgrnam.called is True
    assert mock_setgid.called is True


@pytest.mark.usefixtures('reset', 'cleandir')
def test_setgid_same_group():
    cfile = create_config(('', ))
    with mock.patch('os.setgid'):
        Config(cfile).load()
        assert setgid() is None


@pytest.mark.usefixtures('reset', 'cleandir')
@mock.patch('grp.getgrnam', side_effect=KeyError)
def test_setgid_invalid_group(_):
    cfile = create_config(('group=testgroup', ))
    with pytest.raises(SystemExit) as err:
        Config(cfile).load()
        setgid()
    assert str(err.value) == '64'


@pytest.mark.usefixtures('reset', 'cleandir')
def test_setgid_no_perms():
    cfile = create_config(('group=testgroup', ))
    with mock.patch('grp.getgrnam', side_effect=PermissionError), \
            pytest.raises(SystemExit) as err:
        Config(cfile).load()
        setgid()
    assert str(err.value) == '77'


class Pwd(mock.MagicMock):
    pwd_uid = 9000


@pytest.mark.usefixtures('reset', 'cleandir')
def test_setuid():
    cfile = create_config(('user=abc', ))
    with mock.patch('pwd.getpwnam') as mock_getpwnam, \
            mock.patch('os.setuid') as mock_setuid:
        Config(cfile).load()
        setuid()
    assert mock_getpwnam.called is True
    assert mock_setuid.called is True


@pytest.mark.usefixtures('reset', 'cleandir')
def test_setuid_same_user():
    cfile = create_config(('', ))
    with mock.patch('os.setuid'):
        Config(cfile).load()
        assert setuid() is None


@pytest.mark.usefixtures('reset', 'cleandir')
def test_setuid_invalid_user():
    cfile = create_config(('user=testuser', ))
    with mock.patch('pwd.getpwnam', side_effect=KeyError), \
            pytest.raises(SystemExit) as err:
        Config(cfile).load()
        setuid()
    assert str(err.value) == '64'


@pytest.mark.usefixtures('reset', 'cleandir')
def test_setuid_no_perms():
    cfile = create_config(('user=testuser', ))
    with mock.patch('pwd.getpwnam', side_effect=PermissionError), \
            pytest.raises(SystemExit) as err:
        Config(cfile).load()
        setuid()
    assert str(err.value) == '77'


@pytest.mark.usefixtures('reset', 'cleandir')
def test_set_pid_permissions():
    pidfile = os.path.join(os.getcwd(), 'pid.pid')
    cfile = create_config(('user=testuser', 'group=testgroup',
                           'pidfile={}'.format(pidfile)))
    Config(cfile).load()
    with mock.patch('pwd.getpwnam', side_effect=KeyError), \
            pytest.raises(SystemExit) as err:
        pid_permissions()
    assert str(err.value) == '64'
    with mock.patch('grp.getgrgid', side_effect=KeyError), \
            pytest.raises(SystemExit) as err:
        pid_permissions()
    assert str(err.value) == '64'
    with mock.patch('os.chown', side_effect=PermissionError), \
            pytest.raises(SystemExit) as err:
        pid_permissions()
    assert str(err.value) == '64'
