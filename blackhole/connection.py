import errno
import socket
from tornado import iostream
from blackhole.state import MailState
from blackhole.data import response


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
        stream = iostream.IOStream(connection)
        mail_state = MailState()

        def handle(line):
            """
            Handle a line of socket data, figure out if
            it's a valid SMTP keyword and handle it
            accordingly.
            """
            if mail_state.get_reading():
                resp = None
                if line[0] == "." and len(line) == 3 and ord(line[0]) == 46:
                    mail_state.set_reading(False)
                    resp = response(250)
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
                mail_state.set_reading(True)
            else:
                resp = response(500)
            if resp:
                stream.write(resp)
            loop()
            
        def loop():
            """
            Loop over the oscket data until we receive
            a newline character (\n)
            """
            stream.read_until("\n", handle)
            
        stream.write(response(220))
        loop()