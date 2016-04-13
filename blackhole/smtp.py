import asynchat

from blackhole.config import Config


class SmtpHandler(asynchat.async_chat):
    _data = []

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
        data = ''.join(self.data).strip()
        parts = data.split(None, 1)
        if parts:
            verb = parts[0]
            method = self.lookup_handler(verb) or self.handle_UNKNOWN
            method()
        else:
            self.send(501, 'Syntax error')

    def send(self, code, msg):
        self.push("{} {}\r\n".format(code, msg))

    def greet(self):
        self.send(220, 'blackhole.io ESMTP')

    def do_HELO(self):
        self.push(250, 'OK')

    def do_UNKNOWN(self):
        self.push(500, 'Not implemented')
