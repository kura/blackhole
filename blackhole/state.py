class MailState():
    _reading_data = False

    @property
    def reading(self):
        return self._reading_data

    @reading.setter
    def reading(self, val):
        self._reading_data = val
