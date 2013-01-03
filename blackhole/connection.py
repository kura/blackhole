import errno
import socket
import ssl
import sys

from tornado import iostream
from tornado.options import options

from blackhole.state import MailState
from blackhole.data import response
from blackhole.opts import ports
from blackhole.ssl_utils import sslkwargs
from blackhole.log import log


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
            sock.listen(5000)
            socks[s] = sock
        except socket.error, e:
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
    """
    if connection.getsockname()[1] == options.ssl_port and options.ssl:
        try:
            ssl_connection = ssl.wrap_socket(connection, **sslkwargs)
        except (ssl.SSLError, socket.error), e:
            if e.errno == ssl.SSL_ERROR_EOF or e.errno == errno.ECONNABORTED:
                ssl_connection.close()
                return
            else:
                raise
        # Do a nasty blanket Exception until SSL exceptions are fully known
        try:
            return iostream.SSLIOStream(ssl_connection)
        except Exception, e:
            log.error(e)
            ssl_connection.close()
            return
    else:
        return iostream.IOStream(connection)


def handle_command(line, stream, mail_state):
    """Handle each SMTP command as it's sent to the server"""
    if mail_state.reading:
        resp = None
        # Not exactly nice but it's only way I could safely figure
        # out if it was the \n.\n
        if line[0] == "." and len(line) == 3 and ord(line[0]) == 46:
            mail_state.reading = False
            resp = response()
    elif any(line.lower().startswith(e) for e in ['helo', 'ehlo',
                                                  'mail from',
                                                  'rcpt to', 'rset']):
        resp = response(250)
    elif line.lower().startswith("quit"):
        resp = response(221)
        stream.write(resp)
        stream.close()
        return
    elif line.lower().startswith("data"):
        resp = response(354)
        mail_state.reading = True
    else:
        resp = response(500)
    if resp:
        stream.write(resp)


def connection_ready(sock, fd, events):
    """
    Accepts the socket connections and passes them off
    to be handled.
    """
    while True:
        try:
            connection, address = sock.accept()
        except socket.error, e:
            if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
            return

        connection.setblocking(0)
        stream = connection_stream(connection)
        if not stream:
            return
        mail_state = MailState()

        # Sadly there is nothing I can do about the handle and loop
        # fuctions. They have to exist within connection_ready
        def handle(line):
            """
            Handle a line of socket data, figure out if
            it's a valid SMTP keyword and handle it
            accordingly.
            """
            handle_command(line, stream, mail_state)
            loop()

        def loop():
            """
            Loop over the socket data until we receive
            a newline character (\n)
            """
            stream.read_until("\n", handle)

        stream.write(response(220))
        loop()
