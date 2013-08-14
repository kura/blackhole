import unittest

from tornado.options import options

from blackhole.opts import *
from blackhole.connection import handle_command
from blackhole.state import MailState
from blackhole.data import get_response, ACCEPT_RESPONSES,\
    BOUNCE_RESPONSES, OFFLINE_RESPONSES, UNAVAILABLE_RESPONSES,\
    RANDOM_RESPONSES, EHLO_RESPONSES


class TestResponses(unittest.TestCase):
    ok_done = ('250 OK\r\n', False)
    quit = ('221 Thank you for speaking to me\r\n', True)
    data = ('354 Start mail input; end with <CRLF>.<CRLF>\r\n', False)
    unknown = ('500 Command not recognized\r\n', False)
    ok = ('220 OK\r\n', False)
    vrfy = ('252 OK, cannot VRFY user but will attempt delivery\r\n', False)
    ehlo = (['250-OK\r\n', '250-SIZE 512000\r\n', '250-VRFY\r\n',
             '250-STARTTLS\r\n', '250-ENHANCEDSTATUSCODES\r\n',
             '250-8BITMIME\r\n', '250 DSN\r\n'], False)

    def test_handle_command_helo_response(self):
        m = MailState()
        r = handle_command("HELO", m)
        self.assertEqual(self.ok_done[0], r[0])

    def test_handle_command_helo_connection_close(self):
        m = MailState()
        r = handle_command("HELO", m)
        self.assertEqual(self.ok_done[1], r[1])

    def test_handle_command_helo_reading_state(self):
        m = MailState()
        r = handle_command("HELO", m)
        self.assertEqual(m.reading, False)

    def test_handle_command_ehlo_response(self):
        m = MailState()
        r = handle_command("EHLO", m)
        self.assertEqual(self.ehlo[0], r[0])

    def test_handle_command_ehlo_connection_close(self):
        m = MailState()
        r = handle_command("EHLO", m)
        self.assertEqual(self.ehlo[1], r[1])

    def test_handle_command_ehlo_reading_state(self):
        m = MailState()
        r = handle_command("EHLO", m)
        self.assertEqual(m.reading, False)

    def test_handle_command_mail_from_response(self):
        m = MailState()
        r = handle_command("MAIL FROM", m)
        self.assertEqual(self.ok_done[0], r[0])

    def test_handle_command_mail_from_connection_close(self):
        m = MailState()
        r = handle_command("MAIL FROM", m)
        self.assertEqual(self.ok_done[1], r[1])

    def test_handle_command_mail_from_reading_state(self):
        m = MailState()
        r = handle_command("MAIL FROM", m)
        self.assertEqual(m.reading, False)

    def test_handle_command_rcpt_to_response(self):
        m = MailState()
        r = handle_command("RCPT TO", m)
        self.assertEqual(self.ok_done[0], r[0])

    def test_handle_command_rcpt_to_connection_close(self):
        m = MailState()
        r = handle_command("RCPT TO", m)
        self.assertEqual(self.ok_done[1], r[1])

    def test_handle_command_rcpt_to_reading_state(self):
        m = MailState()
        r = handle_command("RCPT TO", m)
        self.assertEqual(m.reading, False)

    def test_handle_command_rset_response(self):
        m = MailState()
        r = handle_command("RSET", m)
        self.assertEqual(self.ok_done[0], r[0])

    def test_handle_command_rset_connection_close(self):
        m = MailState()
        r = handle_command("RSET", m)
        self.assertEqual(self.ok_done[1], r[1])

    def test_handle_command_rset_reading_state(self):
        m = MailState()
        r = handle_command("RSET", m)
        self.assertEqual(m.reading, False)

    def test_handle_command_quit_response(self):
        m = MailState()
        r = handle_command("QUIT", m)
        self.assertEqual(self.quit[0], r[0])

    def test_handle_command_quit_connection_close(self):
        m = MailState()
        r = handle_command("QUIT", m)
        self.assertEqual(self.quit[1], r[1])

    def test_handle_command_quit_reading_state(self):
        m = MailState()
        r = handle_command("QUIT", m)
        self.assertEqual(m.reading, False)

    def test_handle_command_data_response(self):
        m = MailState()
        r = handle_command("DATA", m)
        self.assertEqual(self.data[0], r[0])

    def test_handle_command_data_connection_close(self):
        m = MailState()
        r = handle_command("DATA", m)
        self.assertEqual(self.data[1], r[1])

    def test_handle_command_data_reading_state(self):
        m = MailState()
        r = handle_command("DATA", m)
        self.assertEqual(m.reading, True)

    def test_handle_command_unknown_command_response(self):
        m = MailState()
        r = handle_command("KURA", m)
        self.assertEqual(self.unknown[0], r[0])

    def test_handle_command_unknown_command_connection_close(self):
        m = MailState()
        r = handle_command("KURA", m)
        self.assertEqual(self.unknown[1], r[1])

    def test_handle_command_unknown_command_reading_state(self):
        m = MailState()
        r = handle_command("KURA", m)
        self.assertEqual(m.reading, False)

    def test_handle_command_starttls_response(self):
        m = MailState()
        r = handle_command("STARTTLS", m)
        self.assertEqual(self.ok[0], r[0])

    def test_handle_command_starttls_connection_close(self):
        m = MailState()
        r = handle_command("STARTTLS", m)
        self.assertEqual(self.ok[1], r[1])

    def test_handle_command_starttls_reading_state(self):
        m = MailState()
        r = handle_command("STARTTLS", m)
        self.assertEqual(m.reading, False)

    def test_handle_command_vrfy_response(self):
        m = MailState()
        r = handle_command("VRFY", m)
        self.assertEqual(self.vrfy[0], r[0])

    def test_handle_command_vrfy_connection_close(self):
        m = MailState()
        r = handle_command("VRFY", m)
        self.assertEqual(self.vrfy[1], r[1])

    def test_handle_command_vrfy_reading_state(self):
        m = MailState()
        r = handle_command("VRFY", m)
        self.assertEqual(m.reading, False)

    def test_handle_command_data_after_data_command_response(self):
        m = MailState()
        m.reading = True
        r = handle_command("Kura Kura Kura", m)
        self.assertEqual(None, r[0])

    def test_handle_command_data_after_data_command_connection_close(self):
        m = MailState()
        r = handle_command("VRFY", m)
        self.assertEqual(False, r[1])


class TestGetAcceptResponse(unittest.TestCase):

    def setUp(self):
        options.mode = "accept"

    def test_get_accept_response(self):
        self.assertTrue(get_response() in ACCEPT_RESPONSES)


class TestGetBounceResponse(unittest.TestCase):

    def setUp(self):
        options.mode = "bounce"

    def test_get_bounce_response(self):
        self.assertTrue(get_response() in BOUNCE_RESPONSES)


class TestGetOfflineResponse(unittest.TestCase):

    def setUp(self):
        options.mode = "offline"

    def test_get_offline_response(self):
        self.assertTrue(get_response() in OFFLINE_RESPONSES)


class TestGetUnavailableResponse(unittest.TestCase):

    def setUp(self):
        options.mode = "unavailable"

    def test_get_unavailable_response(self):
        self.assertTrue(get_response() in UNAVAILABLE_RESPONSES)


class TestGetRandomResponse(unittest.TestCase):

    def setUp(self):
        options.mode = "random"

    def test_get_random_response(self):
        self.assertTrue(get_response() in RANDOM_RESPONSES)
