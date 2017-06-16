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

import getpass
import grp
import logging
import os
import pathlib
import socket
import time
import unittest
from unittest import mock

import pytest

from blackhole.config import Config, config_test, parse_cmd_args, warn_options
from blackhole.exceptions import ConfigException

from ._utils import (Args, cleandir, create_config, create_file, reset)


@pytest.mark.usefixtures('reset', 'cleandir')
def test_default():
    with mock.patch('getpass.getuser') as mock_getuser, \
            mock.patch('grp.getgrgid') as mock_getgrgid:
        conf = Config()
    assert conf.config_file is None
    assert mock_getuser.called is True
    assert mock_getuser.call_count is 1
    assert mock_getgrgid.called is True
    assert mock_getgrgid.call_count is 1


@pytest.mark.usefixtures('reset', 'cleandir')
def test_no_access():
    conf = Config()
    conf.config_file = pathlib.PurePath('/fake/file.conf')
    with mock.patch('os.access', return_value=False) as mock_os_access, \
            pytest.raises(ConfigException):
        conf.load()
    assert mock_os_access.called is True
    assert mock_os_access.call_count is 1


@pytest.mark.usefixtures('reset', 'cleandir')
def test_load():
    cfile = create_config(('#not=thisline', 'listen=10.0.0.1:1025',
                           'mode=bounce   #default accept'))
    conf = Config(cfile).load()
    assert conf.listen == [('10.0.0.1', 1025, socket.AF_INET, {})]
    assert conf.tls_listen == []
    cfile = create_config(('#not=thisline', 'listen=10.0.0.1:1025',
                           '''this won't be added''',
                           'mode=bounce   #default accept'))
    with pytest.raises(ConfigException):
        Config(cfile).load()


@pytest.mark.usefixtures('reset', 'cleandir')
def test_load_none():
    conf = Config(None).load()
    assert conf.mode == 'accept'
    assert conf.workers is 1


@pytest.mark.usefixtures('reset', 'cleandir')
def test_warnings():
    settings = (('tls_listen', (1, 2)), ('tls_dhparams', None),
                ('user', 'root'), ('group', 'root'))
    conf = Args(settings)
    args = Args()
    args.less_secure = True
    conf.args = args
    mmock = mock.MagicMock(spec=logging)
    with mock.patch('os.getuid', return_value=0), \
        mock.patch('os.getgid', return_value=0), \
            mock.patch('logging.getLogger', return_value=mmock):
        warn_options(conf)
    assert mmock.warning.call_count == 3


@pytest.mark.usefixtures('reset', 'cleandir')
def test_invalid_options():
    cfile = create_config(('workers=2', 'delay=10', 'test=option'))
    with pytest.raises(ConfigException):
        Config(cfile).load()


@pytest.mark.usefixtures('reset', 'cleandir')
class TestCmdParser(unittest.TestCase):

    def test_default_conf(self):
        parser = parse_cmd_args(['-c/fake/file.conf'])
        assert parser.config_file == '/fake/file.conf'
        parser = parse_cmd_args(['--conf=/fake/file.conf'])
        assert parser.config_file == '/fake/file.conf'

    def test_version(self):
        with pytest.raises(SystemExit) as exc:
            parse_cmd_args(['-v'])
        assert str(exc.value) == '0'
        with pytest.raises(SystemExit) as exc:
            parse_cmd_args(['--version'])
        assert str(exc.value) == '0'

    def test_test(self):
        parser = parse_cmd_args(['-t'])
        assert parser.test is True
        parser = parse_cmd_args(['--test'])
        assert parser.test is True

    def test_debug(self):
        parser = parse_cmd_args(['-d'])
        assert parser.debug is True
        parser = parse_cmd_args(['--debug'])
        assert parser.debug is True

    def test_background(self):
        parser = parse_cmd_args(['-b'])
        assert parser.background is True
        parser = parse_cmd_args(['--background'])
        assert parser.background is True


@pytest.mark.usefixtures('reset', 'cleandir')
class TestConfigTest(unittest.TestCase):

    def test_config_test(self):
        key = create_file('key.key')
        cert = create_file('crt.crt')
        user = getpass.getuser()
        group = grp.getgrgid(os.getgid()).gr_name
        settings = ('listen=0.0.0.0:1205', 'user={}'.format(user),
                    'group={}'.format(group), 'timeout=180',
                    'tls_listen=0.0.0.0:1465',
                    'tls_cert={}'.format(cert), 'tls_key={}'.format(key),
                    'delay=10', 'mode=bounce', 'workers=2')
        cfile = create_config(settings)
        args = Args((('less_secure', True), ('config_file', cfile)))
        with mock.patch('blackhole.config.Config.test_port',
                        return_value=True), \
            mock.patch('blackhole.config.Config.test_tls_port',
                       return_value=True), \
                pytest.raises(SystemExit) as exc:
            config_test(args)
        assert str(exc.value) == '0'


@pytest.mark.usefixtures('reset', 'cleandir')
class TestListen(unittest.TestCase):

    def test_default(self):
        cfile = create_config(('', ))
        conf = Config(cfile).load()
        with mock.patch('socket.has_ipv6', False):
            assert conf.listen == [('127.0.0.1', 25, socket.AF_INET, {}),
                                   ('127.0.0.1', 587, socket.AF_INET, {})]
        with mock.patch('socket.has_ipv6', True):
            assert conf.listen == [('127.0.0.1', 25, socket.AF_INET, {}),
                                   ('127.0.0.1', 587, socket.AF_INET, {}),
                                   ('::', 25, socket.AF_INET6, {}),
                                   ('::', 587, socket.AF_INET6, {})]

    def test_localhost(self):
        cfile = create_config(('listen=localhost:25', ))
        conf = Config(cfile).load()
        assert conf.listen == [('localhost', 25, socket.AF_INET, {})]

    def test_ipv6_disabled(self):
        cfile = create_config(('listen=:::25', ))
        conf = Config(cfile).load()
        conf._listen = [('::', 25, socket.AF_UNSPEC, {})]
        with pytest.raises(ConfigException), \
                mock.patch('socket.has_ipv6', False):
            conf.test_ipv6_support()

    @unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
    def test_ipv6(self):
        cfile = create_config(('listen=:::25', ))
        conf = Config(cfile).load()
        assert conf.listen == [('::', 25, socket.AF_INET6, {})]

    def test_no_flags(self):
        cfile = create_config(('listen=:25', ))
        conf = Config(cfile).load()
        assert conf.listen == [('', 25, socket.AF_INET, {})]

    def test_mode_flag(self):
        cfile = create_config(('listen=:25 mode=bounce', ))
        conf = Config(cfile).load()
        assert conf.listen == [('', 25, socket.AF_INET, {'mode': 'bounce'})]

    def test_delay_flag(self):
        cfile = create_config(('listen=:25 delay=30', ))
        conf = Config(cfile).load()
        assert conf.listen == [('', 25, socket.AF_INET, {'delay': '30'})]

    def test_delay_range_flag(self):
        cfile = create_config(('listen=:25 delay=30-50', ))
        conf = Config(cfile).load()
        assert conf.listen == [('', 25, socket.AF_INET,
                               {'delay': ('30', '50')})]

    def test_mode_and_delay_range_flag(self):
        cfile = create_config(('listen=:25 delay=15-20 mode=bounce', ))
        conf = Config(cfile).load()
        assert conf.listen == [('', 25, socket.AF_INET, {'delay': ('15', '20'),
                                                         'mode': 'bounce'})]

    def test_listen_flags_special_ipv4(self):
        cfile = create_config(('listen=:25 mode=bounce', ))
        conf = Config(cfile).load()
        assert conf.flags_from_listener('127.0.0.1', 25) == {'mode': 'bounce'}
        assert conf.flags_from_listener('0.0.0.0', 25) == {'mode': 'bounce'}

    def test_listen_flags_special_ipv6(self):
        cfile = create_config(('listen=:::25 mode=bounce', ))
        conf = Config(cfile).load()
        assert conf.flags_from_listener('::1', 25) == {'mode': 'bounce'}


@pytest.mark.usefixtures('reset', 'cleandir')
class TestPort(unittest.TestCase):

    def test_str_port(self):
        cfile = create_config(('listen=127.0.0.1:abc', ))
        with pytest.raises(ConfigException):
            Config(cfile).load()

    def test_lower_than_min(self):
        cfile = create_config(('listen=127.0.0.1:0', ))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_port()

    def test_larger_than_max(self):
        cfile = create_config(('listen=127.0.0.1:99999', ))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_port()

    def test_port_under_1024_no_perms(self):
        cfile = create_config(('listen=127.0.0.1:1023', ))
        conf = Config(cfile).load()
        with mock.patch('os.getuid', return_value=9000) as mock_getuid, \
                pytest.raises(ConfigException):
            conf.test_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1

    def test_port_under_1024_with_perms_available(self):
        cfile = create_config(('listen=127.0.0.1:1024', ))
        conf = Config(cfile).load()
        with mock.patch('os.getuid', return_value=0) as mock_getuid, \
                mock.patch('socket.socket.bind', return_value=True):
            conf.test_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1

    @unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
    def test_ipv4_and_ipv6_same_port(self):
        cfile = create_config(('listen=127.0.0.1:9000,:::9000', ))
        conf = Config(cfile).load()
        assert conf.listen == [('127.0.0.1', 9000, socket.AF_INET, {}),
                               ('::', 9000, socket.AF_INET6, {})]

    @unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
    def test_ipv4_and_ipv6_diff_port(self):
        cfile = create_config(('listen=127.0.0.1:9000,:::9001', ))
        conf = Config(cfile).load()
        assert conf.listen == [('127.0.0.1', 9000, socket.AF_INET, {}),
                               ('::', 9001, socket.AF_INET6, {})]

    def test_port_under_1024_with_perms_unavailable(self):
        cfile = create_config(('listen=127.0.0.1:1023', ))
        conf = Config(cfile).load()
        with mock.patch('os.getuid', return_value=0) as mock_getuid, \
            mock.patch('socket.socket.bind',
                       side_effect=OSError(1, 'none')) as mock_socket, \
                pytest.raises(ConfigException):
            conf.test_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1
        assert mock_socket.called is True
        assert mock_socket.call_count is 1

    def test_port_over_1023_available(self):
        cfile = create_config(('listen=127.0.0.1:1024', ))
        conf = Config(cfile).load()
        with mock.patch('os.getuid', return_value=9000) as mock_getuid, \
                mock.patch('socket.socket.bind', return_value=True):
            conf.test_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1

    def test_port_over_1023_unavailable(self):
        cfile = create_config(('listen=127.0.0.1:1024', ))
        conf = Config(cfile).load()
        with mock.patch('os.getuid', return_value=9000) as mock_getuid, \
            mock.patch('socket.socket.bind',
                       side_effect=OSError(1, 'none')) as mock_socket, \
                pytest.raises(ConfigException):
            conf.test_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1
        assert mock_socket.called is True
        assert mock_socket.call_count is 1


@pytest.mark.usefixtures('reset', 'cleandir')
class TestUser(unittest.TestCase):

    def test_invalid_user(self):
        user = time.monotonic()
        cfile = create_config(('user={}'.format(user), ))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_user()

    def test_valid_user(self):
        cfile = create_config(('user={}'.format(getpass.getuser()), ))
        conf = Config(cfile).load()
        assert conf.user == getpass.getuser()


@pytest.mark.usefixtures('reset', 'cleandir')
class TestGroup(unittest.TestCase):

    def test_invalid_group(self):
        group = time.monotonic()
        cfile = create_config(('group={}'.format(group), ))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_group()

    def test_valid_group(self):
        gname = grp.getgrgid(os.getgid()).gr_name
        cfile = create_config(('group={}'.format(gname), ))
        conf = Config(cfile).load()
        assert conf.group == grp.getgrgid(os.getgid()).gr_name


@pytest.mark.usefixtures('reset', 'cleandir')
class TestTimeout(unittest.TestCase):

    def test_default_timeout(self):
        cfile = create_config(('', ))
        conf = Config(cfile).load()
        assert conf.timeout == 60

    def test_str_timeout(self):
        cfile = create_config(('timeout=xcbsfbsrwgrwgsgrsgsdgrwty4y4fsg', ))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_timeout()

    def test_valid_timeout(self):
        cfile = create_config(('timeout=10', ))
        conf = Config(cfile).load()
        assert conf.timeout == 10

    def test_timeout_over_180(self):
        cfile = create_config(('timeout=300', ))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_timeout()


@pytest.mark.usefixtures('reset', 'cleandir')
class TestTlsPort(unittest.TestCase):

    def test_default_tls_port(self):
        cfile = create_config(('', ))
        conf = Config(cfile).load()
        assert conf.tls_listen == []

    def test_str_tls_port(self):
        cfile = create_config(('tls_listen=127.0.0.1:abc', ))
        with pytest.raises(ConfigException):
            Config(cfile).load()

    def test_same_port_tls_port(self):
        cfile = create_config(('listen=127.0.0.1:25',
                               'tls_listen=127.0.0.1:25', ))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_port()

    def test_valid_tls_port(self):
        cfile = create_config(('tls_listen=127.0.0.1:19', ))
        conf = Config(cfile).load()
        assert conf.tls_listen == [('127.0.0.1', 19, socket.AF_INET, {})]

    def test_tls_lower_than_min(self):
        cfile = create_config(('tls_listen=127.0.0.1:0', ))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_port()

    def test_tls_larger_than_max(self):
        cfile = create_config(('tls_listen=127.0.0.1:99999', ))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_port()

    def test_tls_under_1024_no_perms(self):
        cfile = create_config(('tls_listen=127.0.0.1:1023', ))
        conf = Config(cfile).load()
        with mock.patch('os.getuid', return_value=9000) as mock_getuid, \
                pytest.raises(ConfigException):
            conf.test_tls_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1

    def test_tls_under_1024_with_perms_available(self):
        cfile = create_config(('tls_listen=127.0.0.1:1024', ))
        conf = Config(cfile).load()
        with mock.patch('os.getuid', return_value=0) as mock_getuid, \
                mock.patch('socket.socket.bind', return_value=True):
            conf.test_tls_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1

    def test_tls_under_1024_with_perms_unavailable(self):
        cfile = create_config(('tls_listen=127.0.0.1:1023', ))
        conf = Config(cfile).load()
        with mock.patch('os.getuid', return_value=0) as mock_getuid, \
            mock.patch('socket.socket.bind',
                       side_effect=OSError(1, 'none')) as mock_socket, \
                pytest.raises(ConfigException):
            conf.test_tls_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1
        assert mock_socket.called is True
        assert mock_socket.call_count is 1

    def test_tls_over_1023_available(self):
        cfile = create_config(('tls_listen=127.0.0.1:1024', ))
        conf = Config(cfile).load()
        with mock.patch('os.getuid', return_value=9000) as mock_getuid, \
                mock.patch('socket.socket.bind', return_value=True):
            conf.test_tls_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1

    def test_tls_over_1023_unavailable(self):
        cfile = create_config(('tls_listen=127.0.0.1:1024', ))
        conf = Config(cfile).load()
        with mock.patch('os.getuid', return_value=9000) as mock_getuid, \
            mock.patch('socket.socket.bind',
                       side_effect=OSError(1, 'none')) as mock_socket, \
                pytest.raises(ConfigException):
            conf.test_tls_port()
        assert mock_getuid.called is True
        assert mock_getuid.call_count is 1
        assert mock_socket.called is True
        assert mock_socket.call_count is 1

    @unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
    def test_ipv4_and_ipv6_same_port(self):
        cfile = create_config(('tls_listen=127.0.0.1:9000,:::9000', ))
        conf = Config(cfile).load()
        assert conf.tls_listen == [('127.0.0.1', 9000, socket.AF_INET, {}),
                                   ('::', 9000, socket.AF_INET6, {})]

    @unittest.skipIf(socket.has_ipv6 is False, 'No IPv6 support')
    def test_ipv4_and_ipv6_diff_port(self):
        cfile = create_config(('tls_listen=127.0.0.1:9000,:::9001', ))
        conf = Config(cfile).load()
        assert conf.tls_listen == [('127.0.0.1', 9000, socket.AF_INET, {}),
                                   ('::', 9001, socket.AF_INET6, {})]


@pytest.mark.usefixtures('reset', 'cleandir')
class TestTls(unittest.TestCase):

    def test_disabled(self):
        cfile = create_config(('', ))
        conf = Config(cfile).load()
        assert conf.test_tls_settings() is None

    def test_ipv6_disabled(self):
        cfile = create_config(('tls_listen=:::465', ))
        conf = Config(cfile).load()
        conf._tls_listen = [('::', 465, socket.AF_UNSPEC, {})]
        with pytest.raises(ConfigException), \
                mock.patch('socket.has_ipv6', False):
            conf.test_tls_ipv6_support()

    def test_port_no_certkey(self):
        settings = ('tls_listen=127.0.0.1:123',)
        cfile = create_config(settings)
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_settings()
        assert conf.tls_listen == [('127.0.0.1', 123, socket.AF_INET, {})]
        assert conf.tls_cert is None
        assert conf.tls_key is None

    def test_cert_no_port_key(self):
        cert = create_file('crt.crt')
        settings = ('tls_cert={}'.format(cert),)
        cfile = create_config(settings)
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_settings()
        assert conf.tls_listen == []
        assert conf.tls_cert == pathlib.PurePath(cert)
        assert conf.tls_key is None

    def test_key_no_port_cert(self):
        key = create_file('key.key')
        settings = ('tls_key={}'.format(key),)
        cfile = create_config(settings)
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_settings()
        assert conf.tls_listen == []
        assert conf.tls_cert is None
        assert conf.tls_key == pathlib.PurePath(key)

    def test_cert_key_no_port(self):
        cert = create_file('crt.crt')
        key = create_file('key.key')
        settings = ('tls_cert={}'.format(cert),
                    'tls_key={}'.format(key))
        cfile = create_config(settings)
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_settings()
        assert conf.tls_listen == []
        assert conf.tls_cert == pathlib.PurePath(cert)
        assert conf.tls_key == pathlib.PurePath(key)

    def test_port_cert_no_key(self):
        cert = create_file('crt.crt')
        settings = ('tls_listen=127.0.0.1:123', 'tls_cert={}'.format(cert),)
        cfile = create_config(settings)
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_settings()
        assert conf.tls_listen == [('127.0.0.1', 123, socket.AF_INET, {})]
        assert conf.tls_cert == pathlib.PurePath(cert)
        assert conf.tls_key is None

    def test_port_key_no_cert(self):
        key = create_file('key.key')
        settings = ('tls_listen=127.0.0.1:123', 'tls_key={}'.format(key))
        cfile = create_config(settings)
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_settings()
        assert conf.tls_listen == [('127.0.0.1', 123, socket.AF_INET, {})]
        assert conf.tls_cert is None
        assert conf.tls_key == pathlib.PurePath(key)

    def test_port_cert_key(self):
        key = create_file('key.key')
        cert = create_file('crt.crt')
        settings = ('tls_listen=127.0.0.1:123', 'tls_cert={}'.format(cert),
                    'tls_key={}'.format(key))
        cfile = create_config(settings)
        conf = Config(cfile).load()
        conf.test_tls_settings()
        assert conf.tls_listen == [('127.0.0.1', 123, socket.AF_INET, {})]
        assert conf.tls_cert == pathlib.PurePath(cert)
        assert conf.tls_key == pathlib.PurePath(key)

    def test_default_dhparam(self):
        cfile = create_config(('', ))
        conf = Config(cfile).load()
        assert conf.tls_dhparams is None

    def test_dhparam_works(self):
        dhparams = create_file('dhparams.pem')
        cfile = create_config(('tls_dhparams={}'.format(dhparams), ))
        conf = Config(cfile).load()
        assert conf.tls_dhparams == pathlib.PurePath(dhparams)

    def test_dhparam_no_exist(self):
        cfile = create_config(('tls_dhparams=/fake/path/dhparams.pem', ))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_tls_dhparams()

    def test_no_flags(self):
        key = create_file('key.key')
        cert = create_file('crt.crt')
        settings = ('tls_listen=:123', 'tls_cert={}'.format(cert),
                    'tls_key={}'.format(key))
        cfile = create_config(settings)
        conf = Config(cfile).load()
        assert conf.tls_listen == [('', 123, socket.AF_INET, {})]

    def test_mode_flag(self):
        key = create_file('key.key')
        cert = create_file('crt.crt')
        settings = ('tls_listen=:123 mode=bounce', 'tls_cert={}'.format(cert),
                    'tls_key={}'.format(key))
        cfile = create_config(settings)
        conf = Config(cfile).load()
        assert conf.tls_listen == [('', 123, socket.AF_INET,
                                   {'mode': 'bounce'})]

    def test_delay_flag(self):
        key = create_file('key.key')
        cert = create_file('crt.crt')
        settings = ('tls_listen=:123 delay=30', 'tls_cert={}'.format(cert),
                    'tls_key={}'.format(key))
        cfile = create_config(settings)
        conf = Config(cfile).load()
        assert conf.tls_listen == [('', 123, socket.AF_INET, {'delay': '30'})]

    def test_delay_range_flag(self):
        key = create_file('key.key')
        cert = create_file('crt.crt')
        settings = ('tls_listen=:123 delay=30-50', 'tls_cert={}'.format(cert),
                    'tls_key={}'.format(key))
        cfile = create_config(settings)
        conf = Config(cfile).load()
        assert conf.tls_listen == [('', 123, socket.AF_INET,
                                   {'delay': ('30', '50')})]

    def test_mode_and_delay_range_flag(self):
        key = create_file('key.key')
        cert = create_file('crt.crt')
        settings = ('tls_listen=:123 mode=bounce delay=15-20',
                    'tls_cert={}'.format(cert), 'tls_key={}'.format(key))
        cfile = create_config(settings)
        conf = Config(cfile).load()
        assert conf.tls_listen == [('', 123, socket.AF_INET,
                                   {'delay': ('15', '20'), 'mode': 'bounce'})]

    def test_tls_listen_flags_special_ipv4(self):
        cfile = create_config(('tls_listen=:465 mode=bounce', ))
        conf = Config(cfile).load()
        assert conf.flags_from_listener('127.0.0.1', 465) == {'mode': 'bounce'}
        assert conf.flags_from_listener('0.0.0.0', 465) == {'mode': 'bounce'}

    def test_tls_listen_flags_special_ipv6(self):
        cfile = create_config(('listen=:::465 mode=bounce', ))
        conf = Config(cfile).load()
        assert conf.flags_from_listener('::1', 465) == {'mode': 'bounce'}


@pytest.mark.usefixtures('reset', 'cleandir')
class TestDelay(unittest.TestCase):

    def test_no_delay(self):
        cfile = create_config(('', ))
        conf = Config(cfile).load()
        assert conf.test_delay() is None
        assert conf.delay is None

    def test_delay_longer_than_timeout(self):
        cfile = create_config(('timeout=10', 'delay=20'))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            assert conf.test_delay()
        assert conf.delay > conf.timeout

    def test_delay(self):
        cfile = create_config(('timeout=30', 'delay=5'))
        conf = Config(cfile).load()
        assert conf.timeout > conf.delay

    def test_delay_over_60(self):
        cfile = create_config(('timeout=70', 'delay=70'))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_delay()
        assert conf.delay is 70


@pytest.mark.usefixtures('reset', 'cleandir')
class TestMode(unittest.TestCase):

    def test_default(self):
        cfile = create_config(('', ))
        conf = Config(cfile).load()
        assert conf.mode == 'accept'

    def test_invalid_mode(self):
        cfile = create_config(('mode=kura', ))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            assert conf.test_mode()
        assert conf.mode == 'kura'

    def test_accept(self):
        cfile = create_config(('mode=accept', ))
        conf = Config(cfile).load()
        assert conf.mode == 'accept'

    def test_bounce(self):
        cfile = create_config(('mode=bounce', ))
        conf = Config(cfile).load()
        assert conf.mode == 'bounce'

    def test_random(self):
        cfile = create_config(('mode=random', ))
        conf = Config(cfile).load()
        assert conf.mode == 'random'


@pytest.mark.usefixtures('reset', 'cleandir')
class TestMaxMessageSize(unittest.TestCase):

    def test_no_size(self):
        cfile = create_config(('', ))
        conf = Config(cfile).load()
        assert conf.max_message_size == 512000

    def test_invalid_size(self):
        cfile = create_config(('max_message_size=abc', ))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_max_message_size()

    def test_size(self):
        cfile = create_config(('max_message_size=1024000', ))
        conf = Config(cfile).load()
        assert conf.max_message_size == 1024000
        assert conf.test_max_message_size() is None


@pytest.mark.usefixtures('reset', 'cleandir')
class TestPidfile(unittest.TestCase):

    def test_pidfile_default(self):
        cfile = create_config(('', ))
        conf = Config(cfile).load()
        assert conf.pidfile == pathlib.PurePath('/tmp/blackhole.pid')

    def test_pidfile_no_permission(self):
        cfile = create_config(('pidfile=/fake/path.pid', ))
        conf = Config(cfile).load()
        with pytest.raises(ConfigException):
            conf.test_pidfile()

    def test_pidfile_with_permission(self):
        cfile = create_config(('pidfile=/tmp/path.pid', ))
        conf = Config(cfile).load()
        with mock.patch('builtins.open', return_value=True):
            conf.test_pidfile()


@pytest.mark.usefixtures('reset', 'cleandir')
class TestDynamicSwitch(unittest.TestCase):

    def test_dynamic_switch_default(self):
        cfile = create_config(('', ))
        conf = Config(cfile).load()
        assert conf.dynamic_switch is True

    def test_dynamic_switch_false(self):
        cfile = create_config(('dynamic_switch=false', ))
        conf = Config(cfile).load()
        assert conf.dynamic_switch is False

    def test_dynamic_switch_invalid(self):
        cfile = create_config(('dynamic_switch=abc', ))
        with pytest.raises(ConfigException):
            conf = Config(cfile).load()
        cfile = create_config(('', ))
        conf = Config(cfile).load()
        conf._dynamic_switch = 'abc'
        with pytest.raises(ConfigException):
            conf.test_dynamic_switch()


@pytest.mark.usefixtures('reset', 'cleandir')
class TestWorkers(unittest.TestCase):

    def test_default(self):
        conf = Config(None).load()
        assert conf.workers == 1

    def test_more_than_cpus(self):
        conf = Config(None).load()
        with mock.patch('multiprocessing.cpu_count', return_value=0), \
                pytest.raises(ConfigException):
            conf.test_workers()

    def test_ok(self):
        cfile = create_config(('workers=4', ))
        conf = Config(cfile).load()
        with mock.patch('multiprocessing.cpu_count', return_value=4):
            conf.test_workers()
        assert conf.workers is 4
