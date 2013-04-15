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
        self.email_id = None
