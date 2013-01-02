import errno
import socket
import ssl

from tornado import iostream
from tornado.options import options

from blackhole.state import MailState
from blackhole.data import response
from blackhole.opts import ports
from blackhole.ssl_utils import sslkwargs


def sockets():
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
                log.error("Permission denied, could not bind to %s:%s" % (options.host, port))
            else:
                log.error(e)
            sys.exit(1)
    return socks


def connection_ready(sock, fd, events):
    """
    Accepts the socket connections and passes them off
    to be handled.
    """
    while True:
        try:
            connection, address = sock.accept()
        except socket.error, e:
            if e[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
            return

        connection.setblocking(0)
        if connection.getsockname()[1] == options.ssl_port and options.ssl:
            try:
                print sslkwargs
                ssl_connection = ssl.wrap_socket(connection, **sslkwargs)
            except (ssl.SSLError, socket.error), err:
                if err.args[0] == ssl.SSL_ERROR_EOF or err.args[0] == errno.ECONNABORTED:
                    ssl_connection.close()
                    return
                else:
                    raise
            # Do a nasty blanket Exception until SSL exceptions are fully known
            try:
                stream = iostream.SSLIOStream(ssl_connection)
            except Exception, e:
                log.error(e)
                ssl_connection.close()
                return
        else:
            stream = iostream.IOStream(connection)
        mail_state = MailState()

        def handle(line):
            """
            Handle a line of socket data, figure out if
            it's a valid SMTP keyword and handle it
            accordingly.
            """
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
                print resp
                stream.write(resp)
            loop()

        def loop():
            """
            Loop over the socket data until we receive
            a newline character (\n)
            """
            stream.read_until("\n", handle)

        stream.write(response(220))
        loop()
