class MailState():
    _reading_data = False

    def set_reading(self, val):
        self._reading_data = val

    @property
    def reading(self):
        return self._reading_data
