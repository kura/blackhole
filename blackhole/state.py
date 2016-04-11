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

"""blackhole.state - State object for the current connection."""

from blackhole.opts import options
from blackhole.utils import message_id


class MailState(object):
    """A state object used for remembering
    the current connections place in our runtime.

    This is mostly used for figuring out if we're
    receiving SMTP commands or have trigger the
    DATA command.
    """
    _reading_data = False
    _message_id = None
    _connection = None
    _stream = None
    _closed = False
    _timeout = None
    _history = []
    _mode = 'accept'

    def __init__(self, connection, stream):
        self.message_id = message_id()
        self.connection = connection
        self.stream = stream

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value

    @mode.deleter
    def mode(self):
        self._mode = 'accept'

    @property
    def closed(self):
        return self._closed

    @closed.setter
    def closed(self, val):
        self._closed = val

    @closed.deleter
    def closed(self):
        self._closed = False

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout

    @timeout.deleter
    def timeout(self):
        self._timeout = None

    @property
    def data(self):
        return self._history[-1]

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, val):
        self._history.append(val)
        # only store the last 10 items
        self._history = self._history[-10:]

    @history.deleter
    def history(self):
        self._history = []

    @property
    def reading(self):
        """
        MailState's 'reading' property, used for
        figuring out where we are in the state chain.
        """
        return self._reading_data

    @reading.setter
    def reading(self, val):
        """Property for setting self.reading

        'val' is a bool."""
        self._reading_data = val

    @reading.deleter
    def reading(self):
        """Property for deleting self.reading"""
        # This shouldn't be called or need to be called
        del self._reading_data

    @property
    def message_id(self):
        """
        Email ID is used to assign commands
        sent and received against an email/connection
        ID.

        Only utilized when debug flag is set.
        """
        return self._message_id

    @message_id.setter
    def message_id(self, val):
        """
        Set email_id

        'val' is a hexidecimal string.
        """
        self._message_id = val

    @message_id.deleter
    def message_id(self):
        """Reset email_id back to None."""
        self._message_id = None

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, conn):
        self._connection = conn

    @connection.deleter
    def connection(self):
        del self._connection

    @property
    def stream(self):
        """
        Steamed is an instance of
        tornado.iostream.IOStream or
        tornado.iostream.SSLIOStream if
        the socket is SSL-enabled.

        This can be overidden on-the-fly for example
        STARTTLS does that.
        """
        return self._stream

    @stream.setter
    def stream(self, val):
        """
        Set the stream

        'val' is an instance of
        tornado.iostream.IOStream or
        tornado.iostream.SSLIOStream
        """
        self._stream = val

    @stream.deleter
    def stream(self):
        """Reset the stream back to None"""
        self._stream = None
