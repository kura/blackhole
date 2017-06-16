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

import asyncio
import unittest
from unittest import mock

import pytest

from blackhole.config import Config
from blackhole.exceptions import BlackholeRuntimeException
from blackhole.supervisor import Supervisor

from ._utils import (Args, cleandir, create_config, create_file, reset)

try:
    import ssl
except ImportError:
    ssl = None





@pytest.mark.usefixtures('reset', 'cleandir')
def test_spawn_ipv4():
    cfile = create_config(('listen=127.0.0.1:9999', ))
    Config(cfile).load()
    with mock.patch('socket.socket.bind'):
        supervisor = Supervisor()
    assert len(supervisor.socks) == 1


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_spawn_ipv4_tls():
    cert = create_file('cert.pem')
    key = create_file('key.key')
    cfile = create_config(('listen=127.0.0.1:9998',
                           'tls_listen=127.0.0.1:9999',
                           'tls_cert={}'.format(cert),
                           'tls_key={}'.format(key)))
    conf = Config(cfile).load()
    conf.args = Args((('less_secure', True), ))
    with mock.patch('socket.socket.bind'), \
            mock.patch('ssl.create_default_context'):
        supervisor = Supervisor()
    assert len(supervisor.socks) == 2


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_spawn_ipv6_tls():
    cert = create_file('cert.pem')
    key = create_file('key.key')
    cfile = create_config(('listen=::9998',
                           'tls_listen=:::9999',
                           'tls_cert={}'.format(cert),
                           'tls_key={}'.format(key)))
    conf = Config(cfile).load()
    conf.args = Args((('less_secure', True), ))
    with mock.patch('socket.socket.bind'), \
            mock.patch('ssl.create_default_context'):
        supervisor = Supervisor()
    assert len(supervisor.socks) == 2


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_spawn_ipv4_tls_less_secure():
    cert = create_file('cert.pem')
    key = create_file('key.key')
    cfile = create_config(('listen=127.0.0.1:9998',
                           'tls_listen=127.0.0.1:9999',
                           'tls_cert={}'.format(cert),
                           'tls_key={}'.format(key)))
    conf = Config(cfile).load()
    conf.args = Args((('less_secure', False), ))
    with mock.patch('socket.socket.bind'), \
            mock.patch('ssl.create_default_context'):
        supervisor = Supervisor()
    assert len(supervisor.socks) == 2


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_spawn_ipv6_tls_less_secure():
    cert = create_file('cert.pem')
    key = create_file('key.key')
    cfile = create_config(('listen=::9998',
                           'tls_listen=:::9999',
                           'tls_cert={}'.format(cert),
                           'tls_key={}'.format(key)))
    conf = Config(cfile).load()
    conf.args = Args((('less_secure', False), ))
    with mock.patch('socket.socket.bind'), \
            mock.patch('ssl.create_default_context'):
        supervisor = Supervisor()
    assert len(supervisor.socks) == 2


key_data = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAtkJc/03E/Q32Oj6ixcTiY9BxWPBLaoGXqS1eSnZXIgHVfKwQ
8QyVb433hxtEYrTgrgHzFIfThf8f0ZISyPCtTXVJwBv08TeQXE2iGbHsFDKFGG9m
fDC+Cx6t8uKne81x2dCHXHeoUDKm1ae+FyUFhqMfM5Zp0AJZLueUw+8ooO5aJDCj
Jq+QgTnaFY/ZjpNK22hbRGBoUMJWUykvQMle7X52WQqrRkNIcqTvqYUCaGWqUV63
+3U9AgbuejOuZ+43MmZGdvpJSVyBVbkmeklbtD27dDrxRm4EC+LpUdpiXDIO1fLp
cj0ibuDArwZd0h6Lc7eDiOHdiv3EVlr29JZS9wIDAQABAoIBACOrVTv54mWMB/Za
L8z4vT2/m49GZ9wORLotUNjN1DuplDh0DFTAm7ZbWGguo/GVaKtlYkdQVctRpM6F
AfwlbiVMoQRh9EwJDc2iu+i/c254fKfNlYcUmvzeIjj4tsJ58KAqOXOVT3FymEgU
LhWlfzFcV0znUQoOi5msZOb7tT3ZUz8PJz8P30HaERLbLTTYR3qWdnS4ASlvfpX4
BnqPwQmi7NebNgXdlc3JhVYFtHna+iNkas7vXESw2Y1L491QpT2bgCAexs5VKe34
gnRnKzugzaX5E/3Kpyrsadp/cnIVHW7OUq+BLXvLZVJo7Y+oyMHvzpDMI87xnXQn
BqGLdsECgYEA5iCD3f7g3lTGBnfqYk1SwhTOlW9O4jsRodYtmLZHdswxdDppwaHN
oHVS1dL7xjWHMgAw7ia9sQWdi9xVLbHWAS4NiWzUlGa7Y30kKFZCspp6FdDVAl+l
nYkJe63XhPUSzIj8HGPRF0ouEwXWQG8frmZOIRco/v+MzuK1sf9ANUcCgYEAysAf
xTslUExIBGDYSAfHdCkKuPRvfspuFHbIe5+9WqEzpnSIcyQ/c/Kiy2gPRd4sCFZR
O341ljRGnGqVoKmMw11kFKtSZbQ0StoXFHojfUD2wfcX+OdeZYWIQfOA8ysDU07D
6h7pShN5sRkJJ43myLgiMvf0k2+Cb3LWbw+4jNECgYAn2r27tqaPGrNo71+iQq3w
etYEP1C0EXLOSl9/MSJTSq3N6Ufjhvgrr+X2riF4hFCzsiDHPeJgRA6y6CfAUCo1
7hneEQEH6nrNkiCu87F9aQ93s8EQNixiihcgWk0W87KbxaWT7R2LIQe1t68RXa1o
8MLbLD2nW+6w7cZ12zTthQKBgQCFCy+N3/LrTzMO1HH4SkqCmg/0MEodnD5B5XRH
UxoRJ6jZ+Kw1SjrtHfHfoggro8+nJOUnMfl9+A3BxFstUzUQWe87dPSb0nViDNyK
Tl+NaJzDyR4M8d5KpiY0iNI8PyRufUgoEGKrfj4jjTcpon8nhVTDt1vhh5HDCktW
E63ZkQKBgEr0x4bNIuCStpJwkFn6Zh8xnThCwnhH0MH0KOOzVevYTFAy8u8KbSOw
e2G8VWGmY/GoGUleHqqXLSi6UereS4TEBMh7ZzLhc5OGoljgO4dLyxvKu3eyfjGX
4KX04JK3CyPeNdL0/UIlMdTdWV17eTpfQ8hOwOVxPWJo5iiO4Knx
-----END RSA PRIVATE KEY-----"""
cert_data = """-----BEGIN CERTIFICATE-----
MIIDBjCCAe4CCQC+JlUbr0pa8zANBgkqhkiG9w0BAQsFADBFMQswCQYDVQQGEwJB
VTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50ZXJuZXQgV2lkZ2l0
cyBQdHkgTHRkMB4XDTE2MDUwMTIzMDgzN1oXDTE2MDUzMTIzMDgzN1owRTELMAkG
A1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoMGEludGVybmV0
IFdpZGdpdHMgUHR5IEx0ZDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEB
ALZCXP9NxP0N9jo+osXE4mPQcVjwS2qBl6ktXkp2VyIB1XysEPEMlW+N94cbRGK0
4K4B8xSH04X/H9GSEsjwrU11ScAb9PE3kFxNohmx7BQyhRhvZnwwvgserfLip3vN
cdnQh1x3qFAyptWnvhclBYajHzOWadACWS7nlMPvKKDuWiQwoyavkIE52hWP2Y6T
SttoW0RgaFDCVlMpL0DJXu1+dlkKq0ZDSHKk76mFAmhlqlFet/t1PQIG7nozrmfu
NzJmRnb6SUlcgVW5JnpJW7Q9u3Q68UZuBAvi6VHaYlwyDtXy6XI9Im7gwK8GXdIe
i3O3g4jh3Yr9xFZa9vSWUvcCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEALQVsOsbm
T13SX07yZ49+A0MSalX9u4QMe2L/bonYEs2/TB4dads7EPrZmhfGQ5cQlHaKp+U3
ZCGqlMMrsEWtYu3Ovc2DLJTykccb5gJV/eAvt8siBH1+8EVuwptz4KBAPbosxtaZ
ITeGcU/K5Sg6VcVqmEB1Bam7jYyk91f42mtqINS3QmtBhGDCDyGLu13N0Tcli4Ex
tG2AOVmjWihvNmd21SLOJoQDn+8C04j5sTWVfLxRbfwFyP/frhAYN4EfHVHLjHf/
n3ZYIxa8EMbZyJNQfipZeBUrAyYtjgHCRfgM2t5TscMfB1ewrQ/iDSNE5a65vYOC
VMr7S68leXh3Aw==
-----END CERTIFICATE-----"""
dhparams_data = """-----BEGIN DH PARAMETERS-----
MEYCQQDkC0FDza65yPJj8HeXOpoR315XGC+/5uaJpw5CevVwAmRns3TEuFwTal5H
MWsNrHaep9EbyJ00JW/cSoaECAYLAgEC
-----END DH PARAMETERS-----"""


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_spawn_ipv4_tls_dhparams():
    cert = create_file('test.pem', cert_data)
    key = create_file('test.key', key_data)
    dhparams = create_file('dhparams.pem', dhparams_data)
    cfile = create_config(('listen=127.0.0.1:9998',
                           'tls_listen=127.0.0.1:9999',
                           'tls_cert={}'.format(cert),
                           'tls_key={}'.format(key),
                           'tls_dhparams={}'.format(dhparams)))
    conf = Config(cfile).load()
    conf.args = Args((('less_secure', False), ))
    with mock.patch('socket.socket.bind'):
        supervisor = Supervisor()
    assert len(supervisor.socks) == 2


@unittest.skipIf(ssl is None, 'No ssl module')
@pytest.mark.usefixtures('reset', 'cleandir')
def test_spawn_ipv6_tls_dhparams():
    cert = create_file('test.pem', cert_data)
    key = create_file('test.key', key_data)
    dhparams = create_file('dhparams.pem', dhparams_data)
    cfile = create_config(('listen=:::9998',
                           'tls_listen=:::9999',
                           'tls_cert={}'.format(cert),
                           'tls_key={}'.format(key),
                           'tls_dhparams={}'.format(dhparams)))
    conf = Config(cfile).load()
    conf.args = Args((('less_secure', False), ))
    with mock.patch('socket.socket.bind'):
        supervisor = Supervisor()
    assert len(supervisor.socks) == 2
    assert supervisor.socks[1]['ssl'] is not None


@pytest.mark.usefixtures('reset', 'cleandir')
def test_spawn_ipv6():
    cfile = create_config(('listen=:::9999', ))
    Config(cfile).load()
    with mock.patch('socket.socket.bind'):
        supervisor = Supervisor()
    assert len(supervisor.socks) == 1


@pytest.mark.usefixtures('reset', 'cleandir')
def test_spawn_ipv4_and_ipv6():
    cfile = create_config(('listen=:9999, :::9999', ))
    Config(cfile).load()
    supervisor = Supervisor()
    with mock.patch('socket.socket.bind'):
        supervisor = Supervisor()
    assert len(supervisor.socks) == 2


@pytest.mark.usefixtures('reset', 'cleandir')
def test_spawn_ipv4_fail():
    cfile = create_config(('listen=:9999', ))
    Config(cfile).load()
    with mock.patch('socket.socket.bind', side_effect=OSError), \
            pytest.raises(BlackholeRuntimeException):
        Supervisor()


@pytest.mark.usefixtures('reset', 'cleandir')
def test_spawn_ipv6_fail():
    cfile = create_config(('listen=:::9999', ))
    Config(cfile).load()
    with mock.patch('socket.socket.bind', side_effect=OSError), \
            pytest.raises(BlackholeRuntimeException):
        Supervisor()


@pytest.mark.usefixtures('reset', 'cleandir')
def test_spawn_ipv4_and_ipv6_fail():
    cfile = create_config(('listen=:9999, :::9999', ))
    Config(cfile).load()
    with mock.patch('socket.socket.bind', side_effect=OSError), \
            pytest.raises(BlackholeRuntimeException):
        Supervisor()


@pytest.mark.usefixtures('reset', 'cleandir')
def test_create():
    cfile = create_config(('listen=:9999, :::9999', 'workers=2', ))
    Config(cfile).load()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with mock.patch('socket.socket.bind'), \
            mock.patch('blackhole.worker.Worker.start'):
        supervisor = Supervisor(loop=loop)
        supervisor.start_workers()
        assert len(supervisor.workers) == 2
    loop.stop()


@pytest.mark.usefixtures('reset', 'cleandir')
def test_run():
    cfile = create_config(('listen=:9999, :::9999', 'workers=2', ))
    Config(cfile).load()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with mock.patch('socket.socket.bind'), \
            mock.patch('blackhole.worker.Worker.start'):
        supervisor = Supervisor(loop)
        with mock.patch('asyncio.unix_events._UnixSelectorEventLoop.'
                        'run_forever'):
            supervisor.run()
        assert len(supervisor.workers) == 2
    supervisor.loop.stop()


@pytest.mark.usefixtures('reset', 'cleandir')
def test_stop():
    cfile = create_config(('listen=:9999, :::9999', 'workers=2', ))
    Config(cfile).load()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with mock.patch('socket.socket.bind'), \
            mock.patch('blackhole.worker.Worker.start'):
        supervisor = Supervisor(loop)
        supervisor.start_workers()
        assert len(supervisor.workers) == 2
        with mock.patch('blackhole.worker.Worker.stop') as mock_stop, \
                pytest.raises(SystemExit) as err:
            supervisor.stop()
    assert mock_stop.call_count == 2
    assert str(err.value) == '0'
    supervisor.loop.stop()


@pytest.mark.usefixtures('reset', 'cleandir')
def test_stop_runtime_error():
    cfile = create_config(('listen=:9999, :::9999', 'workers=2', ))
    Config(cfile).load()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with mock.patch('socket.socket.bind'), \
            mock.patch('blackhole.worker.Worker.start'):
        supervisor = Supervisor(loop)
        supervisor.start_workers()
        assert len(supervisor.workers) == 2
        with mock.patch('blackhole.worker.Worker.stop') as mock_stop, \
                mock.patch('asyncio.unix_events._UnixSelectorEventLoop.'
                           'stop',
                           side_effect=RuntimeError) as mock_rt, \
                pytest.raises(SystemExit) as err:
            supervisor.stop()
    assert mock_rt.call_count == 1
    assert mock_stop.call_count == 2
    assert str(err.value) == '0'
    supervisor.loop.stop()
