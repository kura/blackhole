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

"""blackhole.connection - Provide mechanisms for processing socket data.

This module provides methods for Blackhole to use internally
for binding and listening on sockets as well as process all
incoming socket data and responding appropriately."""

import errno
import re
import socket

# ssl check
try:
    import ssl
except ImportError:
    ssl = None
import sys
import time

from tornado import (gen, iostream)
from tornado.ioloop import IOLoop
from tornado.options import options

from blackhole.state import MailState
from blackhole.data import (response, response_message, get_response,
                            EHLO_RESPONSES, MODES, ACCEPT_RESPONSES,
                            BOUNCE_RESPONSES, OFFLINE_RESPONSES,
                            UNAVAILABLE_RESPONSES, RANDOM_RESPONSES)
from blackhole.opts import ports
from blackhole.ssl_utils import sslkwargs
from blackhole.log import log
from blackhole.utils import (mailname, message_id)


def sockets():
    """
    Spawn a looper which loops over socket data and creates the sockets.

    It should only ever loop over a maximum of two - standard (std)
    and SSL (ssl).

    This way we're able to detect incoming connection vectors and
    handle them accordingly.

    A dictionary of sockets is then returned to later be added to
    the IOLoop.
    """
    socks = {}
    for aport in ports():
        try:
            port = options.ssl_port if aport == "ssl" else options.port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setblocking(0)
            sock.bind((options.host, port))
            sock.listen(5)
            socks[aport] = sock
        except socket.error as err:
            if err.errno == 13:
                log.error("Permission denied, could not bind to %s:%s",
                          options.host, port)
            else:
                log.error(err)
            sys.exit(1)
    return socks


def connection_stream(connection):
    """
    Create an IOStream from a connection.

    Detect which socket the connection is being made on,
    create and iostream for the connection, wrapping it
    in SSL if connected over the SSL socket.

    The parameter 'connection' is an instance of 'socket'
    from stdlib.
    """
    if connection.getsockname()[1] == options.ssl_port and options.ssl:
        return ssl_connection(connection)
    else:
        return iostream.IOStream(connection)


def ssl_connection(connection):
    if ssl is None:
        return
    try:
        ssl_conn = ssl.wrap_socket(connection, **sslkwargs)
        return iostream.SSLIOStream(ssl_conn)
    except (ssl.SSLError, socket.error) as err:
        if err.errno == ssl.SSL_ERROR_EOF or err.errno == errno.ECONNABORTED:
            ssl_conn.close()
            return


def switch_response_mode(mail_state):
    if options.switch_mode:
        data = mail_state.data
        _, text = data.split(":")
        _, domain = text.split("@")
        bits = domain.split('.')
        if bits[0] in MODES:
            mail_state.mode = bits[0]


def handle_UNKNOWN(mail_state):
    write_response(mail_state, response(500))


def handle_EHLO(mail_state):
    resps = ["250-{}\r\n".format(mailname())]
    if options.ssl:
        resps.append("250-STARTTLS\r\n")
    for key, val in enumerate(EHLO_RESPONSES):
        val = val.format(options.message_size_limit) if key == 0 else val
        resps.append("{}\r\n".format(val))
    for resp in resps:
        write_response(mail_state, resp)


def handle_HELO(mail_state):
    write_response(mail_state, response(250))


def handle_MAIL(mail_state):
    switch_response_mode(mail_state)
    write_response(mail_state, response(250))


def handle_RCPT(mail_state):
    switch_response_mode(mail_state)
    write_response(mail_state, response(250))


def handle_NOOP(mail_state):
    write_response(mail_state, response(250))


def handle_RSET(mail_state):
    mail_state.message_id = message_id()
    mail_state.reading = False
    write_response(mail_state, response(250))


def handle_STARTTLS(mail_state):
    if not ssl or not options.ssl:
        write_response(mail_state, response(500))
        return
    fileno = mail_state.stream.socket.fileno()
    IOLoop.current().remove_handler(fileno)
    mail_state.stream = ssl_connection(mail_state.connection)
    write_response(mail_state, response(252))


def handle_VRFY(mail_state):
    write_response(mail_state, response(252))


def handle_QUIT(mail_state):
    write_response(mail_state, response(221))
    mail_state.stream.close()
    mail_state.closed = True
    del mail_state.stream


def handle_DATA(mail_state):
    mail_state.reading = True
    write_response(mail_state, response(354))


def handle_reading(mail_state):
    prev = "".join(mail_state.history[-2:])
    if prev == "\r\n.\r\n":
        mail_state.reading = False
        if options.switch_mode:
            mode = mail_state.mode
        else:
            mode = options.mode
        rresp = get_response(mode)
        resp = response_message(rresp)
        write_response(mail_state, resp)


def handle_greeting(mail_state):
    greeting = "220 {}\r\n".format(mailname())
    write_response(mail_state, greeting)


def lookup_handler(command):
    mod = sys.modules[__name__]
    cmd = "handle_{}".format(command.upper())
    return getattr(mod, cmd, None)


def handle_command(mail_state):
    r"""Handle each SMTP command as it's sent to the server.

    The paramater 'line' is the currently stream of data
    ending in '\r\n'.
    'mail_state' is an instance of 'blackhole.state.MailState'.
    """
    if mail_state.reading:
        handle_reading(mail_state)
    else:
        data = mail_state.data.strip()
        parts = data.split(None, 1)
        if parts:
            method = lookup_handler(parts[0]) or handle_UNKNOWN
            method(mail_state)
        else:
            write_response(mail_state, response(501))


def write_response(mail_state, resp):
    """Write the response back to the stream"""
    log.debug("[%s] SEND: %s", mail_state.message_id, resp.upper().rstrip())
    mail_state.stream.write(resp)


@gen.coroutine
def connection_ready(sock, *args):
    """
    Handle socket connections.

    'sock' is an instance of 'socket'.
    'filedesc' is an open file descriptor for the current connection.
    'events' is an integer of the number of events on the socket.
    """
    try:
        connection, address = sock.accept()
    except socket.error as err:
        if err.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
            raise
        return

    log.debug("Connection from '%s'", address[0])

    connection.setblocking(0)
    stream = connection_stream(connection)
    # No stream, bail out
    if not stream:
        return

    def _on_timeout():
        """Time out inactive connections."""
        write_response(mail_state, '421 Timeout\r\n')
        mail_state.stream.close()

    mail_state = MailState(connection, stream)

    def handle(line):
        """Handle a line of socket data."""
        IOLoop.instance().remove_timeout(mail_state.timeout)
        mail_state.history = line
        log.debug("[%s] RECV: %s", mail_state.message_id, mail_state.data)
        handle_command(mail_state)
        if mail_state.closed is True:
            return
        else:
            loop()

    def loop():
        r"""Loop over the socket data until we receive \r\n ."""
        timeout = time.time() + options.timeout
        mail_state.timeout = IOLoop.instance().add_timeout(timeout,
                                                           _on_timeout)
        # Protection against stream already reading exceptions
        if not mail_state.stream.reading():
            mail_state.stream.read_until("\r\n", handle)

    handle_greeting(mail_state)
    loop()
