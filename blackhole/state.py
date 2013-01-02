class MailState():
    _reading_data = False

    @property
    def reading(self):
    	"""
    	MailState's 'reading' property, used for
    	figuring out where we are in the state chain.
    	"""
        return self._reading_data

    @reading.setter
    def reading(self, val):
    	"""Property for setting self.reading"""
        self._reading_data = val

    @reading.deleter
    def reading(self):
    	"""Property for deleting self.reading"""
    	# This shouldn't be called or need to be called
    	del self._reading_data
