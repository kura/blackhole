"""blackhole.connection - Provide mechanisms for processing socket data.

This module provides methods for Blackhole to use internally
for binding and listening on sockets as well as process all
incoming socket data and responding appropriately."""

import errno
import socket
import ssl
import sys

from tornado import iostream
from tornado.options import options

from blackhole import __fullname__
from blackhole.state import MailState
from blackhole.data import response, EHLO_RESPONSES
from blackhole.opts import ports
from blackhole.ssl_utils import sslkwargs
from blackhole.log import log
from blackhole.utils import email_id, get_mailname


def sockets():
    """
    Spawn a looper which loops over socket data and creates
    the sockets.

    It should only ever loop over a maximum of two - standard (std)
    and SSL (ssl).

    This way we're able to detect incoming connection vectors and
    handle them accordingly.

    A dictionary of sockets is then returned to later be added to
    the IOLoop.
    """
    socks = {}
    for s in ports():
        try:
            port = options.ssl_port if s == "ssl" else options.port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setblocking(0)
            sock.bind((options.host, port))
            sock.listen(5)
            socks[s] = sock
        except socket.error as e:
            if e.errno == 13:
                log.error("Permission denied, could not bind to %s:%s" %
                          (options.host, port))
            else:
                log.error(e)
            sys.exit(1)
    return socks


def connection_stream(connection):
    """
    Detect which socket the connection is being made on,
    create and iostream for the connection, wrapping it
    in SSL if connected over the SSL socket.

    The parameter 'connection' is an instance of 'socket'
    from stdlib.
    """
    if connection.getsockname()[1] == options.ssl_port and options.ssl:
        try:
            ssl_connection = ssl.wrap_socket(connection, **sslkwargs)
        except (ssl.SSLError, socket.error) as e:
            if e.errno == ssl.SSL_ERROR_EOF or e.errno == errno.ECONNABORTED:
                ssl_connection.close()
                return
            else:
                raise
        # Do a nasty blanket Exception until SSL exceptions are fully known
        try:
            return iostream.SSLIOStream(ssl_connection)
        except Exception as e:
            log.error(e)
            ssl_connection.close()
            return
    else:
        return iostream.IOStream(connection)


def handle_command(line, mail_state):
    """Handle each SMTP command as it's sent to the server

    The paramater 'line' is the currently stream of data
    ending in '\\n'.
    'mail_state' is an instance of 'blackhole.state.MailState'.
    """
    close = False
    if mail_state.reading:
        resp = None
        # Not exactly nice but it's only way I could safely figure
        # out if it was the \n.\n
        if line[0] == "." and len(line) == 3 and ord(line[0]) == 46:
            mail_state.reading = False
            resp = response()
            from tornado.ioloop import IOLoop
            import time
            IOLoop.instance().add_timeout(time.time() + 5, time.time())
    elif line.lower().startswith("ehlo"):
        resp = ["%s\r\n" % x for x in EHLO_RESPONSES]
    elif any(line.lower().startswith(e) for e in ['helo', 'mail from',
                                                  'rcpt to', 'noop']):
        resp = response(250)
    elif line.lower().startswith("rset"):
        new_id = email_id()
        log.debug("[%s] RSET received, changing ID to [%s]" %
                  (mail_state.email_id, new_id))
        # Reset mail state
        mail_state.reading = False
        mail_state.email_id = new_id
        resp = response(250)
    elif line.lower().startswith("starttls"):
        resp = response(220)
    elif line.lower().startswith("vrfy"):
        resp = response(252)
    elif line.lower().startswith("quit"):
        resp = response(221)
        close = True
    elif line.lower().startswith("data"):
        resp = response(354)
        mail_state.reading = True
    else:
        resp = response(500)
    
    # this is a blocking action, sadly
    # async non blocking methods did not
    # work. =(
    if options.delay > 0:
        # import has to be called here for
        # some reason...
        import time
        time.sleep(options.delay)
    return resp, close


def write_response(stream, mail_state, resp):
    """Write the response back to the stream"""
    log.debug("[%s] SEND: %s" % (mail_state.email_id, resp.upper().rstrip()))
    stream.write(resp)


def connection_ready(sock, fd, events):
    """
    Accepts the socket connections and passes them off
    to be handled.

    'sock' is an instance of 'socket'.
    'fd' is an open file descriptor for the current connection.
    'events' is an integer of the number of events on the socket.
    """
    while True:
        try:
            connection, address = sock.accept()
        except socket.error as e:
            if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
            return

        log.debug("Connection from '%s'" % address[0])

        connection.setblocking(0)
        stream = connection_stream(connection)
        if not stream:
            return
        mail_state = MailState()
        mail_state.email_id = email_id()

        # Sadly there is nothing I can do about the handle and loop
        # fuctions. They have to exist within connection_ready
        def handle(line):
            """
            Handle a line of socket data, figure out if
            it's a valid SMTP keyword and handle it
            accordingly.
            """
            log.debug("[%s] RECV: %s" % (mail_state.email_id, line.rstrip()))
            resp, close = handle_command(line, mail_state)
            if resp:
                if isinstance(resp, list):
                    # This is required for returning
                    # multiple status codes for EHLO
                    for r in resp:
                        write_response(stream, mail_state, r)
                else:
                    # Otherwise it's a single response
                    write_response(stream, mail_state, resp)
            if close is True:
                log.debug("Closing")
                stream.close()
                return
            else:
                loop()

        def loop():
            """
            Loop over the socket data until we receive
            a newline character (\n)
            """
            stream.read_until("\n", handle)

        hm = "220 %s [%s]\r\n" % (get_mailname(),
                              __fullname__)
        stream.write(hm)
        loop()
