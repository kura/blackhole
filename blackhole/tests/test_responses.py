import unittest

from blackhole.connection import handle_command
from blackhole.state import MailState


class TestResponses(unittest.TestCase):
    ok_done = ('250 2.5.0 OK, done\n', False)
    quit = ('221 2.2.1 Thank you for speaking to me\n', True)
    data = ('354 3.5.4 Start mail input; end with <CRLF>.<CRLF>\n', False)
    unknown = ('500 5.0.0 Command not recognized\n', False)
    ok = ('220 2.2.0 OK, ready\n', False)
    vrfy = ('252 2.5.2 OK, cannot VRFY user but will attempt delivery\n', False)

    def test_handle_command_helo_response(self):
        m = MailState()
        r = handle_command("HELO", m)
        self.assertEqual(self.ok_done[0], r[0])

    def test_handle_command_helo_connection_close(self):
        m = MailState()
        r = handle_command("HELO", m)
        self.assertIs(self.ok_done[1], r[1])

    def test_handle_command_helo_reading_state(self):
        m = MailState()
        r = handle_command("HELO", m)
        self.assertIs(m.reading, False)

    def test_handle_command_ehlo_response(self):
        m = MailState()
        r = handle_command("EHLO", m)
        self.assertEqual(self.ok_done[0], r[0])

    def test_handle_command_ehlo_connection_close(self):
        m = MailState()
        r = handle_command("EHLO", m)
        self.assertIs(self.ok_done[1], r[1])

    def test_handle_command_ehlo_reading_state(self):
        m = MailState()
        r = handle_command("EHLO", m)
        self.assertIs(m.reading, False)

    def test_handle_command_mail_from_response(self):
        m = MailState()
        r = handle_command("MAIL FROM", m)
        self.assertEqual(self.ok_done[0], r[0])

    def test_handle_command_mail_from_connection_close(self):
        m = MailState()
        r = handle_command("MAIL FROM", m)
        self.assertIs(self.ok_done[1], r[1])

    def test_handle_command_mail_from_reading_state(self):
        m = MailState()
        r = handle_command("MAIL FROM", m)
        self.assertIs(m.reading, False)

    def test_handle_command_rcpt_to_response(self):
        m = MailState()
        r = handle_command("RCPT TO", m)
        self.assertEqual(self.ok_done[0], r[0])

    def test_handle_command_rcpt_to_connection_close(self):
        m = MailState()
        r = handle_command("RCPT TO", m)
        self.assertIs(self.ok_done[1], r[1])

    def test_handle_command_rcpt_to_reading_state(self):
        m = MailState()
        r = handle_command("RCPT TO", m)
        self.assertIs(m.reading, False)

    def test_handle_command_rset_response(self):
        m = MailState()
        r = handle_command("RSET", m)
        self.assertEqual(self.ok_done[0], r[0])

    def test_handle_command_rset_connection_close(self):
        m = MailState()
        r = handle_command("RSET", m)
        self.assertIs(self.ok_done[1], r[1])

    def test_handle_command_rset_reading_state(self):
        m = MailState()
        r = handle_command("RSET", m)
        self.assertIs(m.reading, False)

    def test_handle_command_quit_response(self):
        m = MailState()
        r = handle_command("QUIT", m)
        self.assertEqual(self.quit[0], r[0])

    def test_handle_command_quit_connection_close(self):
        m = MailState()
        r = handle_command("QUIT", m)
        self.assertIs(self.quit[1], r[1])

    def test_handle_command_quit_reading_state(self):
        m = MailState()
        r = handle_command("QUIT", m)
        self.assertIs(m.reading, False)

    def test_handle_command_data_response(self):
        m = MailState()
        r = handle_command("DATA", m)
        self.assertEqual(self.data[0], r[0])

    def test_handle_command_data_connection_close(self):
        m = MailState()
        r = handle_command("DATA", m)
        self.assertIs(self.data[1], r[1])

    def test_handle_command_data_reading_state(self):
        m = MailState()
        r = handle_command("DATA", m)
        self.assertIs(m.reading, True)

    def test_handle_command_unknown_command_response(self):
        m = MailState()
        r = handle_command("KURA", m)
        self.assertEqual(self.unknown[0], r[0])

    def test_handle_command_unknown_command_connection_close(self):
        m = MailState()
        r = handle_command("KURA", m)
        self.assertIs(self.unknown[1], r[1])

    def test_handle_command_unknown_command_reading_state(self):
        m = MailState()
        r = handle_command("KURA", m)
        self.assertIs(m.reading, False)

    def test_handle_command_starttls_response(self):
        m = MailState()
        r = handle_command("STARTTLS", m)
        self.assertEqual(self.ok[0], r[0])

    def test_handle_command_starttls_connection_close(self):
        m = MailState()
        r = handle_command("STARTTLS", m)
        self.assertIs(self.ok[1], r[1])

    def test_handle_command_starttls_reading_state(self):
        m = MailState()
        r = handle_command("STARTTLS", m)
        self.assertIs(m.reading, False)

    def test_handle_command_vrfy_response(self):
        m = MailState()
        r = handle_command("VRFY", m)
        self.assertEqual(self.vrfy[0], r[0])

    def test_handle_command_vrfy_connection_close(self):
        m = MailState()
        r = handle_command("VRFY", m)
        self.assertIs(self.vrfy[1], r[1])

    def test_handle_command_vrfy_reading_state(self):
        m = MailState()
        r = handle_command("VRFY", m)
        self.assertIs(m.reading, False)

    def test_handle_command_data_after_data_command_response(self):
        m = MailState()
        m.reading = True
        r = handle_command("Kura Kura Kura", m)
        self.assertIs(None, r[0])

    def test_handle_command_data_after_data_command_connection_close(self):
        m = MailState()
        r = handle_command("VRFY", m)
        self.assertIs(False, r[1])
