import unittest

from blackhole.utils import email_id


class TestEmailIDGenerator(unittest.TestCase):

    def test_email_id_generator(self):
        self.assertRegexpMatches(email_id(), r"^[A-F0-9]{10}$")
