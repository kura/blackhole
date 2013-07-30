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


class MailState(object):
    """A state object used for remembering
    the current connections place in our runtime.

    This is mostly used for figuring out if we're
    receiving SMTP commands or have trigger the
    DATA command.
    """
    _reading_data = False
    _email_id = None
    _stream = None

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
    def email_id(self):
        """
        Email ID is used to assign commands
        sent and received against an email/connection
        ID.

        Only utilized when debug flag is set.
        """
        return self._email_id

    @email_id.setter
    def email_id(self, val):
        """
        Set email_id

        'val' is a hexidecimal string.
        """
        self._email_id = val

    @email_id.deleter
    def email_id(self):
        """Reset email_id back to None."""
        self._email_id = None

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
