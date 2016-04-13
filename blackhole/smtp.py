import asynchat

from blackhole.config import Config
from blackhole.utils import (mailname, message_id)


class SmtpHandler(asynchat.async_chat):
    _data = []
    _data_cmd = False

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data.append(value)

    @data.deleter
    def data(self):
        del self._data
        self._data = []

    def __init__(self, sock):
        self.config = Config()
        asynchat.async_chat.__init__(self, sock)
        self.mailname = mailname()
        self.message_id = message_id()
        self.greet()
        self.set_terminator('\r\n')
        return

    def collect_incoming_data(self, data):
        self.data = data

    def found_terminator(self):
        self.process_data()

    def lookup_handler(self, verb):
        cmd = "do_{}".format(verb.upper())
        return getattr(self, cmd, None)

    def process_data(self):
        if self._data_cmd:
            self.handle_data_command()
            return
        data = ''.join(self.data).strip()
        parts = data.split(None, 1)
        if parts:
            verb = parts[0]
            method = self.lookup_handler(verb) or self.handle_UNKNOWN
            method()
        else:
            self.send(501, 'Syntax error')
        del self.data

    def handle_data_command(self):
        self._data_cmd = False
        self.puush(250, '2.0.0 OK: queued as {}'.format(self.message_id))
        self.set_terminator('\r\n')

    def puush(self, code, msg):
        self.push("{} {}\r\n".format(code, msg))

    def greet(self):
        self.puush(220, '{} ESMTP'.format(self.mailname))

    def do_HELO(self):
        self.puush(250, 'OK')

    def do_EHLO(self):
        self.push("250-{}".format(self.mailname))
        responses = ["250-SIZE 512000", "250-VRFY", "250-ENHANCEDSTATUSCODES",
                     "250-8BITMIME", "250 DSN"]
        for response in responses:
            self.push("{}\r\n".format(response))

    def do_MAIL(self):
        self.puush(250, '2.1.0 OK')

    def do_RCPT(self):
        self.puush(250, '2.1.5 OK')

    def do_DATA(self):
        self._data_cmd = True
        self.set_terminator('\r\n.\r\n')
        self.puush(354, 'End data with <CR><LF>.<CR><LF>')

    def do_NOOP(self):
        self.puush(250, '2.0.0 OK')

    def do_RSET(self):
        self.message_id = message_id()
        self.puush(250, '2.0.0 OK')

    def do_VRFY(self):
        self.puush(252, '2.0.0 OK')

    def do_QUIT(self):
        self.puush(221, '2.0.0 Goodbye')
        self.close()

    def do_UNKNOWN(self):
        self.puush(500, 'Not implemented')
