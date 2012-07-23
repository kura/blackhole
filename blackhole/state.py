
class MailState():
    _reading_data = False

    def set_reading(self, val):
        self._reading_data = val

    def get_reading(self):
        return self._reading_data
