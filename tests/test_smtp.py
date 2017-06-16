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
import inspect
import socket
import threading
import time
import unittest
from smtplib import SMTP, SMTPNotSupportedError, SMTPServerDisconnected
from unittest import mock

import pytest

from blackhole.config import Config
from blackhole.control import _socket
from blackhole.smtp import Smtp

from ._utils import (Args, cleandir, create_config, create_file, reset)


@pytest.mark.usefixtures('reset', 'cleandir')
def test_initiation():
    cfile = create_config(('', ))
    with mock.patch('os.access', return_value=False), \
            mock.patch('socket.getfqdn', return_value='a.blackhole.io'):
        conf = Config(cfile)
    conf.load()
    smtp = Smtp([])
    assert smtp.fqdn == 'a.blackhole.io'


@pytest.mark.usefixtures('reset', 'cleandir')
def test_auth_mechanisms():
    smtp = Smtp([])
    assert smtp.get_auth_members() == ['CRAM-MD5', 'LOGIN', 'PLAIN']


@pytest.mark.usefixtures('reset', 'cleandir')
def test_handler_lookup():
    smtp = Smtp([])
    assert smtp.lookup_handler('AUTH CRAM-MD5') == smtp.auth_CRAM_MD5
    assert smtp.lookup_handler('AUTH LOGIN') == smtp.auth_LOGIN
    assert smtp.lookup_handler('AUTH PLAIN') == smtp.auth_PLAIN
    assert smtp.lookup_handler('AUTH') == smtp.auth_UNKNOWN
    assert smtp.lookup_handler('AUTH KURA') == smtp.auth_UNKNOWN
    assert smtp.lookup_handler('HELP') == smtp.do_HELP
    assert smtp.lookup_handler('DATA') == smtp.do_DATA
    assert smtp.lookup_handler('EHLO') == smtp.do_EHLO
    assert smtp.lookup_handler('ETRN') == smtp.do_ETRN
    assert smtp.lookup_handler('EXPN') == smtp.do_EXPN
    assert smtp.lookup_handler('HELO') == smtp.do_HELO
    assert smtp.lookup_handler('MAIL') == smtp.do_MAIL
    assert smtp.lookup_handler('NOOP') == smtp.do_NOOP
    assert smtp.lookup_handler('QUIT') == smtp.do_QUIT
    assert smtp.lookup_handler('RCPT') == smtp.do_RCPT
    assert smtp.lookup_handler('RSET') == smtp.do_RSET
    assert smtp.lookup_handler('VRFY') == smtp.do_VRFY
    assert smtp.lookup_handler('STARTTLS') == smtp.do_STARTTLS
    assert smtp.lookup_handler('KURA') == smtp.do_UNKNOWN
    assert smtp.lookup_handler('') == smtp.do_UNKNOWN
    assert smtp.lookup_handler('STARTTLS') == smtp.do_STARTTLS
    assert smtp.lookup_handler('HELP DATA') == smtp.help_DATA
    assert smtp.lookup_handler('HELP EHLO') == smtp.help_EHLO
    assert smtp.lookup_handler('HELP ETRN') == smtp.help_ETRN
    assert smtp.lookup_handler('HELP EXPN') == smtp.help_EXPN
    assert smtp.lookup_handler('HELP HELO') == smtp.help_HELO
    assert smtp.lookup_handler('HELP MAIL') == smtp.help_MAIL
    assert smtp.lookup_handler('HELP NOOP') == smtp.help_NOOP
    assert smtp.lookup_handler('HELP QUIT') == smtp.help_QUIT
    assert smtp.lookup_handler('HELP RCPT') == smtp.help_RCPT
    assert smtp.lookup_handler('HELP RSET') == smtp.help_RSET
    assert smtp.lookup_handler('HELP VRFY') == smtp.help_VRFY
    assert smtp.lookup_handler('HELP KURA') == smtp.help_UNKNOWN


@pytest.mark.usefixtures('reset', 'cleandir')
def test_unknown_handlers():
    # Protection against adding/removing without updating tests
    verbs = ['do_DATA', 'do_EHLO', 'do_ETRN', 'do_EXPN', 'do_HELO', 'do_HELP',
             'do_MAIL', 'do_NOOP', 'do_NOT_IMPLEMENTED', 'do_QUIT', 'do_RCPT',
             'do_RSET', 'do_STARTTLS', 'do_UNKNOWN', 'do_VRFY']
    helps = ['help_AUTH', 'help_DATA', 'help_EHLO', 'help_ETRN', 'help_EXPN',
             'help_HELO', 'help_MAIL', 'help_NOOP', 'help_QUIT', 'help_RCPT',
             'help_RSET', 'help_UNKNOWN', 'help_VRFY']
    auths = ['auth_CRAM_MD5', 'auth_LOGIN', 'auth_PLAIN', 'auth_UNKNOWN']
    smtp = Smtp([])
    for mem in inspect.getmembers(smtp, inspect.ismethod):
        f, _ = mem
        if f.startswith('do_'):
            assert f in verbs
        if f.startswith('help_'):
            assert f in helps
        if f.startswith('auth_'):
            assert f in auths


@pytest.mark.usefixtures('reset', 'cleandir')
class Controller:

    def __init__(self, sock=None, loop=None):
        if sock is not None:
            self.sock = sock
        else:
            self.sock = _socket('127.0.0.1', 0, socket.AF_INET)
        self.server = None
        self.loop = asyncio.new_event_loop() if loop is None else loop
        self.thread = None
        self._rsock, self._wsock = socket.socketpair()
        self.loop.add_reader(self._rsock, self._reader)

    def _reader(self):
        self.loop.remove_reader(self._rsock)
        self.loop.stop()
        for task in asyncio.Task.all_tasks(self.loop):
            task.cancel()
        self._rsock.close()
        self._wsock.close()

    def _run(self, ready_event):
        asyncio.set_event_loop(self.loop)
        conf = Config(None)
        conf.mailname = 'blackhole.io'
        _server = self.loop.create_server(lambda: Smtp([]),
                                          sock=self.sock)
        self.server = self.loop.run_until_complete(_server)
        self.loop.call_soon(ready_event.set)
        self.loop.run_forever()
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())
        self.sock.close()
        self.loop.close()

    def start(self):
        ready_event = threading.Event()
        self.thread = threading.Thread(target=self._run, args=(ready_event, ))
        self.thread.daemon = True
        self.thread.start()
        ready_event.wait()

    def stop(self):
        self._wsock.send(b'x')
        self.thread.join()


@pytest.mark.usefixtures('reset', 'cleandir')
@pytest.mark.asyncio
async def test_mode_directive(event_loop, unused_tcp_port):
    cfile = create_config(('listen=:{} mode=bounce'.format(unused_tcp_port), ))
    conf = Config(cfile).load()
    sock = _socket('127.0.0.1', unused_tcp_port, socket.AF_INET)
    controller = Controller(sock)
    controller.start()
    conf.flags_from_listener('127.0.0.1', unused_tcp_port)
    host, port = sock.getsockname()
    with SMTP(host, port) as client:
        msg = ['From: kura@example.com', 'To: kura@example.com',
               'Subject: Test', 'X-Blackhole-Mode: accept',
               'X-Blackhole-Delay: 5', '', 'Testing 1, 2, 3']
        msg = '\n'.join(msg)
        start = time.time()
        code, resp = client.data(msg.encode('utf-8'))
        stop = time.time()
        assert code in [450, 451, 452, 458, 521, 550, 551, 552, 553, 571]
        assert round(stop - start) in (0, 1)
    controller.stop()


@pytest.mark.usefixtures('reset', 'cleandir')
@pytest.mark.asyncio
async def test_delay_directive(event_loop, unused_tcp_port):
    cfile = create_config(('listen=:{} delay=5'.format(unused_tcp_port), ))
    conf = Config(cfile).load()
    sock = _socket('127.0.0.1', unused_tcp_port, socket.AF_INET)
    controller = Controller(sock)
    controller.start()
    conf.flags_from_listener('127.0.0.1', unused_tcp_port)
    host, port = sock.getsockname()
    with SMTP(host, port) as client:
        msg = ['From: kura@example.com', 'To: kura@example.com',
               'Subject: Test', 'X-Blackhole-Mode: bounce',
               'X-Blackhole-Delay: 30', '', 'Testing 1, 2, 3']
        msg = '\n'.join(msg)
        start = time.time()
        code, resp = client.data(msg.encode('utf-8'))
        stop = time.time()
        assert code == 250
        assert round(stop - start) in (4, 5, 6)
    controller.stop()


@pytest.mark.usefixtures('reset', 'cleandir')
@pytest.mark.asyncio
async def test_mode_and_delay_directive(event_loop, unused_tcp_port):
    cfile = create_config(('listen=:{} delay=5 mode=bounce'.format(unused_tcp_port), ))
    conf = Config(cfile).load()
    sock = _socket('127.0.0.1', unused_tcp_port, socket.AF_INET)
    controller = Controller(sock)
    controller.start()
    conf.flags_from_listener('127.0.0.1', unused_tcp_port)
    host, port = sock.getsockname()
    with SMTP(host, port) as client:
        msg = ['From: kura@example.com', 'To: kura@example.com',
               'Subject: Test', 'X-Blackhole-Mode: accept',
               'X-Blackhole-Delay: 30', '', 'Testing 1, 2, 3']
        msg = '\n'.join(msg)
        start = time.time()
        code, resp = client.data(msg.encode('utf-8'))
        stop = time.time()
        assert code in [450, 451, 452, 458, 521, 550, 551, 552, 553, 571]
        assert round(stop - start) in (4, 5, 6)
    controller.stop()


@pytest.mark.usefixtures('reset', 'cleandir')
@pytest.mark.asyncio
async def test_timeout(event_loop):
    cfile = create_config(('timeout=5', ))
    Config(cfile).load()
    controller = Controller()
    controller.start()
    host, port = controller.sock.getsockname()
    with SMTP(host, port) as client:
        await asyncio.sleep(8)
        code, resp = client.helo('example.com')
        assert code == 421
        assert resp == b'Timeout'
    controller.stop()


@pytest.mark.usefixtures('reset', 'cleandir')
@pytest.mark.asyncio
async def test_delay(event_loop):
    cfile = create_config(('timeout=10', ))
    Config(cfile).load()
    controller = Controller()
    controller.start()
    host, port = controller.sock.getsockname()
    with SMTP(host, port) as client:
        msg = ['From: kura@example.com', 'To: kura@example.com',
               'Subject: Test', 'X-Blackhole-Mode: accept',
               'X-Blackhole-Delay: 5', '', 'Testing 1, 2, 3']
        msg = '\n'.join(msg)
        start = time.time()
        code, resp = client.data(msg.encode('utf-8'))
        stop = time.time()
        assert code == 250
        assert resp.startswith(b'2.0.0 OK: queued as')
        assert round(stop - start) in (4, 5, 6)
    controller.stop()


@pytest.mark.usefixtures('reset', 'cleandir')
@pytest.mark.asyncio
async def test_delayed_bounce(event_loop):
    cfile = create_config(('timeout=10', ))
    Config(cfile).load()
    controller = Controller()
    controller.start()
    host, port = controller.sock.getsockname()
    with SMTP(host, port) as client:
        msg = ['From: kura@example.com', 'To: kura@example.com',
               'Subject: Test', 'X-Blackhole-Mode: bounce',
               'X-Blackhole-Delay: 5', '', 'Testing 1, 2, 3']
        msg = '\n'.join(msg)
        start = time.time()
        code, resp = client.data(msg.encode('utf-8'))
        stop = time.time()
        assert code in [450, 451, 452, 458, 521, 550, 551, 552, 553, 571]
        assert round(stop - start) in (4, 5, 6)
    controller.stop()


@pytest.mark.usefixtures('reset', 'cleandir')
@pytest.mark.asyncio
async def test_delay_range(event_loop):
    cfile = create_config(('timeout=10', ))
    Config(cfile).load()
    controller = Controller()
    controller.start()
    host, port = controller.sock.getsockname()
    with SMTP(host, port) as client:
        msg = ['From: kura@example.com', 'To: kura@example.com',
               'Subject: Test', 'X-Blackhole-Mode: accept',
               'X-Blackhole-Delay: 2, 4', '', 'Testing 1, 2, 3']
        msg = '\n'.join(msg)
        start = time.time()
        code, resp = client.data(msg.encode('utf-8'))
        stop = time.time()
        assert code == 250
        assert resp.startswith(b'2.0.0 OK: queued as')
        assert round(stop - start) in (2, 3, 4)
    controller.stop()


@pytest.mark.usefixtures('reset', 'cleandir')
class TestSmtp(unittest.TestCase):

    def setUp(self):
        cfile = create_config(('timeout=5', 'max_message_size=102400'))
        Config(cfile).load()
        controller = Controller()
        controller.start()
        self.host, self.port = controller.sock.getsockname()
        self.addCleanup(controller.stop)

    def test_helo(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.helo('example.com')
            assert code == 250
            assert resp == b'OK'

    def test_ehlo(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.ehlo('example.com')
            assert code == 250
            # resps = resp.decode('utf-8').split('\n')
            eresp = ('blackhole.io', 'HELP', 'PIPELINING',
                     'AUTH CRAM-MD5 LOGIN PLAIN', 'SIZE 102400', 'VRFY',
                     'ETRN', 'ENHANCEDSTATUSCODES', '8BITMIME', 'SMTPUTF8',
                     'EXPN', 'DSN')
            assert resp == '\n'.join(eresp).encode('utf-8')

    def test_mail(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.mail('kura@example.com')
            assert code == 250
            assert resp == b'2.1.0 OK'

    def test_mail_size_ok(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.mail('kura@example.com SIZE=1')
            assert code == 250
            assert resp == b'2.1.0 OK'

    def test_mail_size_ok_and_mime(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.mail('kura@example.com SMTPUTF8 SIZE=1024')
            assert code == 250
            assert resp == b'2.1.0 OK'
        with SMTP(self.host, self.port) as client:
            code, resp = client.mail('kura@example.com BODY=7BIT SIZE=1024')
            assert code == 250
            assert resp == b'2.1.0 OK'
        with SMTP(self.host, self.port) as client:
            code, resp = client.mail('kura@example.com BODY=8BITMIME '
                                     'SIZE=1024')
            assert code == 250
            assert resp == b'2.1.0 OK'

    def test_mail_size_too_large(self):
        with SMTP(self.host, self.port) as client:
            msg = 'MAIL FROM: kura@example.com SIZE=10240000000'
            code, resp = client.docmd(msg)
            assert code == 552
            assert resp == b'Message size exceeds fixed maximum message size'

    def test_mail_size_too_large_and_mime(self):
        with SMTP(self.host, self.port) as client:
            msg = 'MAIL FROM: kura@example.com SMTPUTF8 SIZE=10240000000'
            code, resp = client.docmd(msg)
            assert code == 552
            assert resp == b'Message size exceeds fixed maximum message size'
        with SMTP(self.host, self.port) as client:
            msg = 'MAIL FROM: kura@example.com BODY=7BIT SIZE=10240000000'
            code, resp = client.docmd(msg)
            assert code == 552
            assert resp == b'Message size exceeds fixed maximum message size'
        with SMTP(self.host, self.port) as client:
            msg = 'MAIL FROM: kura@example.com BODY=8BITMIME SIZE=10240000000'
            code, resp = client.docmd(msg)
            assert code == 552
            assert resp == b'Message size exceeds fixed maximum message size'

    def test_mail_smtputf8(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.docmd('MAIL FROM: kura@example.com SMTPUTF8')
            assert code == 250
            assert resp == b'2.1.0 OK'

    def test_mail_7bit(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.docmd('MAIL FROM: kura@example.com BODY=7BIT')
            assert code == 250
            assert resp == b'2.1.0 OK'

    def test_mail_8bitmime(self):
        with SMTP(self.host, self.port) as client:
            msg = 'MAIL FROM: kura@example.com BODY=8BITMIME'
            code, resp = client.docmd(msg)
            assert code == 250
            assert resp == b'2.1.0 OK'

    def test_rcpt(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.rcpt('kura@example.com')
            assert code == 250
            assert resp == b'2.1.5 OK'

    def test_data(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.data(b'testing 1, 2, 3')
            assert code == 250
            assert resp.startswith(b'2.0.0 OK: queued as')

    def test_data_fail(self):
        with SMTP(self.host, self.port) as client:
            msg = ['From: kura@example.com', 'To: kura@example.com',
                   'Subject: Test', 'X-Blackhole-Mode: bounce', '',
                   'Testing 1, 2, 3']
            msg = '\n'.join(msg)
            code, resp = client.data(msg.encode('utf-8'))
            assert code in [450, 451, 452, 458, 521, 550, 551, 552, 553, 571]

    def test_data_random(self):
        with SMTP(self.host, self.port) as client:
            msg = ['From: kura@example.com', 'To: kura@example.com',
                   'Subject: Test', 'X-Blackhole-Mode: random', '',
                   'Testing 1, 2, 3']
            msg = '\n'.join(msg)
            code, resp = client.data(msg.encode('utf-8'))
            assert code in [250, 450, 451, 452, 458, 521, 550, 551, 552, 553,
                            571]

    def test_data_accept(self):
        with SMTP(self.host, self.port) as client:
            msg = ['From: kura@example.com', 'To: kura@example.com',
                   'Subject: Test', 'X-Blackhole-Mode: accept', '',
                   'Testing 1, 2, 3']
            msg = '\n'.join(msg)
            code, resp = client.data(msg.encode('utf-8'))
            assert code == 250
            assert resp.startswith(b'2.0.0 OK: queued as')

    def test_rset(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.rset()
            assert code == 250
            assert resp == b'2.0.0 OK'

    def test_noop(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.noop()
            assert code == 250
            assert resp == b'2.0.0 OK'

    def test_vrfy(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.verify('kura@example.com')
            assert code == 252
            assert resp == b'2.0.0 Will attempt delivery'

    def test_vrfy_pass(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.verify('pass=kura@example.com')
            assert code == 250
            assert resp == b'2.0.0 <pass=kura@example.com> OK'

    def test_vrfy_fail(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.verify('fail=kura@example.com')
            assert code == 550
            assert resp == b'5.7.1 <fail=kura@example.com> unknown'

    def test_expn_no_list(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.expn('')
            assert code == 550
            assert resp == b'Not authorised'

    def test_expn_fail(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.expn('fail=kura@example.com')
            assert code == 550
            assert resp == b'Not authorised'

    def test_expn_list1(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.expn('list1')
            eresp = ('Shadow <shadow@blackhole.io>',
                     'Wednesday <wednesday@blackhole.io>',
                     'Low-key Liesmith <low-key.liesmith@blackhole.io>')
            assert code == 250
            assert resp == '\n'.join(eresp).encode('utf-8')

    def test_expn_list2(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.expn('list2')
            eresp = ('Jim Holden <jim.holden@blackhole.io>',
                     'Naomi Nagata <naomi.nagata@blackhole.io>',
                     'Alex Kamal <alex.kamal@blackhole.io>',
                     'Amos Burton <amos.burton@blackhole.io>')
            assert code == 250
            assert resp == '\n'.join(eresp).encode('utf-8')

    def test_expn_list3(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.expn('list3')
            eresp = ('Takeshi Kovacs <takeshi.kovacs@blackhole.io>',
                     'Laurens Bancroft <laurens.bancroft@blackhole.io>',
                     'Kristin Ortega <kristin.ortega@blackhole.io>',
                     'Quellcrist Falconer <quellcrist.falconer@blackhole.io>',
                     'Virginia Vidaura <virginia.vidaura@blackhole.io>',
                     'Reileen Kawahara <reileen.kawahara@blackhole.io>')
            assert code == 250
            assert resp == '\n'.join(eresp).encode('utf-8')

    def test_expn_all(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.expn('all')
            eresp = ('Takeshi Kovacs <takeshi.kovacs@blackhole.io>',
                     'Laurens Bancroft <laurens.bancroft@blackhole.io>',
                     'Kristin Ortega <kristin.ortega@blackhole.io>',
                     'Quellcrist Falconer <quellcrist.falconer@blackhole.io>',
                     'Virginia Vidaura <virginia.vidaura@blackhole.io>',
                     'Reileen Kawahara <reileen.kawahara@blackhole.io>',
                     'Jim Holden <jim.holden@blackhole.io>',
                     'Naomi Nagata <naomi.nagata@blackhole.io>',
                     'Alex Kamal <alex.kamal@blackhole.io>',
                     'Amos Burton <amos.burton@blackhole.io>',
                     'Shadow <shadow@blackhole.io>',
                     'Wednesday <wednesday@blackhole.io>',
                     'Low-key Liesmith <low-key.liesmith@blackhole.io>')
            assert code == 250
            resps = resp.decode('utf-8').split('\n')
            assert sorted(resps) == sorted(eresp)

    def test_etrn(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.docmd('ETRN')
            assert code == 250
            assert resp == b'Queueing started'

    def test_quit(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.quit()
            assert code == 221
            assert resp == b'2.0.0 Goodbye'

    def test_starttls(self):
        with SMTP(self.host, self.port) as client:
            with pytest.raises(SMTPNotSupportedError):
                code, resp = client.starttls()
            code, resp = client.docmd('STARTTLS')
            assert code == 500
            assert resp == b'Not implemented'

    def test_unknown(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.docmd('KURA')
            assert code == 502
            assert resp == b'5.5.2 Command not recognised'

    def test_help(self):
        with SMTP(self.host, self.port) as client:
            eresp = ('Supported commands: AUTH DATA EHLO ETRN EXPN HELO MAIL '
                     'NOOP QUIT RCPT RSET VRFY')
            assert client.help() == eresp.encode('utf-8')

    def test_help_auth(self):
        with SMTP(self.host, self.port) as client:
            resp = client.help('AUTH')
            assert resp == b'Syntax: AUTH CRAM-MD5 LOGIN PLAIN'

    def test_help_data(self):
        with SMTP(self.host, self.port) as client:
            resp = client.help('DATA')
            assert resp == b'Syntax: DATA'

    def test_help_ehlo(self):
        with SMTP(self.host, self.port) as client:
            resp = client.help('EHLO')
            assert resp == b'Syntax: EHLO domain.tld'

    def test_help_etrn(self):
        with SMTP(self.host, self.port) as client:
            resp = client.help('ETRN')
            assert resp == b'Syntax: ETRN'

    def test_help_expn(self):
        with SMTP(self.host, self.port) as client:
            resp = client.help('EXPN')
            assert resp == b'Syntax: EXPN <list1 | list2 | list3 | all>'

    def test_help_helo(self):
        with SMTP(self.host, self.port) as client:
            resp = client.help('HELO')
            assert resp == b'Syntax: HELO domain.tld'

    def test_help_mail(self):
        with SMTP(self.host, self.port) as client:
            resp = client.help('MAIL')
            assert resp == b'Syntax: MAIL FROM: <address>'

    def test_help_noop(self):
        with SMTP(self.host, self.port) as client:
            resp = client.help('NOOP')
            assert resp == b'Syntax: NOOP'

    def test_help_quit(self):
        with SMTP(self.host, self.port) as client:
            resp = client.help('QUIT')
            assert resp == b'Syntax: QUIT'

    def test_help_rcpt(self):
        with SMTP(self.host, self.port) as client:
            resp = client.help('RCPT')
            assert resp == b'Syntax: RCPT TO: <address>'

    def test_help_rset(self):
        with SMTP(self.host, self.port) as client:
            resp = client.help('RSET')
            assert resp == b'Syntax: RSET'

    def test_help_unknown(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.docmd('HELP', 'KURA')
            eresp = ('Supported commands: AUTH DATA EHLO ETRN EXPN HELO MAIL '
                     'NOOP QUIT RCPT RSET VRFY')
            assert code == 501
            assert resp == eresp.encode('utf-8')

    def test_help_vrfy(self):
        with SMTP(self.host, self.port) as client:
            resp = client.help('VRFY')
            assert resp == b'Syntax: VRFY <address>'

    def test_auth_login(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.docmd('AUTH', 'LOGIN')
            assert code == 334
            assert resp == b'VXNlcm5hbWU6'
            code, resp = client.docmd('test')
            assert code == 235
            assert resp == b'2.7.0 Authentication successful'

    def test_auth_login_fail(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.docmd('AUTH', 'LOGIN')
            assert code == 334
            assert resp == b'VXNlcm5hbWU6'
            code, resp = client.docmd('fail=test')
            assert code == 535
            assert resp == b'5.7.8 Authentication failed'

    def test_auth_login_pass(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.docmd('AUTH', 'LOGIN')
            assert code == 334
            assert resp == b'VXNlcm5hbWU6'
            code, resp = client.docmd('pass=test')
            assert code == 235
            assert resp == b'2.7.0 Authentication successful'

    def test_auth_cram_md5(self):
        with SMTP(self.host, self.port) as client:
            client.user = 'test'
            client.password = 'test'
            code, resp = client.auth('CRAM-MD5', client.auth_cram_md5)
            assert code == 235
            assert resp == b'2.7.0 Authentication successful'

    def test_auth_cram_md5_fail(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.docmd('AUTH', 'CRAM-MD5')
            assert code == 334
            code, resp = client.docmd('fail=test')
            assert code == 535
            assert resp == b'5.7.8 Authentication failed'

    def test_auth_cram_md5_pass(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.docmd('AUTH', 'CRAM-MD5')
            assert code == 334
            code, resp = client.docmd('pass=test')
            assert code == 235
            assert resp == b'2.7.0 Authentication successful'

    def test_auth_plain(self):
        with SMTP(self.host, self.port) as client:
            client.user = 'test'
            client.password = 'test'
            code, resp = client.auth('PLAIN', client.auth_plain)
            assert code == 235
            assert resp == b'2.7.0 Authentication successful'

    def test_auth_plain_fail(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.docmd('AUTH', 'PLAIN')
            assert code == 334
            code, resp = client.docmd('fail=test')
            assert code == 535
            assert resp == b'5.7.8 Authentication failed'

    def test_auth_plain_pass(self):
        with SMTP(self.host, self.port) as client:
            with SMTP(self.host, self.port) as client:
                code, resp = client.docmd('AUTH', 'PLAIN')
                assert code == 334
                code, resp = client.docmd('pass=test')
                assert code == 235
                assert resp == b'2.7.0 Authentication successful'

    def test_auth_plain_fail_oneline(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.docmd('AUTH', 'PLAIN fail=test')
            assert code == 535
            assert resp == b'5.7.8 Authentication failed'

    def test_auth_plain_pass_oneline(self):
        with SMTP(self.host, self.port) as client:
            with SMTP(self.host, self.port) as client:
                code, resp = client.docmd('AUTH', 'PLAIN pass=test')
                assert code == 235
                assert resp == b'2.7.0 Authentication successful'

    def test_auth_unknown(self):
        with SMTP(self.host, self.port) as client:
            code, resp = client.docmd('AUTH', 'KURA')
            assert code == 501
            assert resp == b'5.5.4 Syntax: AUTH mechanism'

    def test_too_many_unknown_commands(self):
        with SMTP(self.host, self.port) as client, \
                pytest.raises(SMTPServerDisconnected):
            for _ in range(11):
                code, resp = client.docmd('KURA')
            assert code == 502
            assert resp == b'5.5.3 Too many unknown commands'
