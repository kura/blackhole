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

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import unittest

from mock import patch

from blackhole.opts import print_help


class TestPrintHelp(unittest.TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help(self, stdout_mock):
        val = """Usage: blackhole [OPTIONS] (start|stop|status)\n\n  -v, """\
              """--version                    Print out program version\n"""\
              """  -h, --help                       Show this help"""\
              """ information\n\nBlackhole\n---------\n\n  --conf=FILE"""\
              """                      Config file to parse and use."""\
              """ Overrides command line args\n  --group=GROUP"""\
              """                    Group to drop privs to during run"""\
              """ time\n  --host=IP                        IP address to"""\
              """ bind go\n  --log=FILE                       """\
              """File to write logs to (not very verbose)\n  """\
              """--message_size_limit=BYTES       Maximum size of a message"""\
              """ in Bytes, returned in EHLO but\n"""\
              """                                     not enforced\n"""\
              """  --pid=FILE                       File to write process"""\
              """ information to\n  --port=PORT                      """\
              """Port to listen for connections on\n  --user=USER"""\
              """                      User to drop privs to during run"""\
              """ time\n\nBlackhole SSL\n-------------\n\n  --ssl=BOOL"""\
              """                       Enable/disable SSL\n"""\
              """  --ssl_cert=PATH                  SSL Certificate\n"""\
              """  --ssl_key=PATH                   SSL Private Key\n"""\
              """  --ssl_port=PORT                  Port to listen for"""\
              """ SSL connections on\n\nDebug\n-----\n\n  --debug=BOOL"""\
              """                     Enable/disable debug logging mode."""\
              """ Causes a lot of disk I/O\n\nDelay\n-----\n\n"""\
              """  --delay=INT                      Delay SMTP connection"""\
              """ for number of seconds passed\n\nMode\n----\n\n"""\
              """  --mode=MODE                      Mode to run blackhole"""\
              """ in (accept, bounce, random,\n"""\
              """                                     unavailable,"""\
              """ offline)\n\n                                   """\
              """accept - accept all email with code 250, 251, 252 or"""\
              """ 253\n                                   bounce -"""\
              """ bounce all email with a random code,\n"""\
              """                                     excluding 250, 251,"""\
              """ 252, 253\n                                   random"""\
              """ - randomly accept or bounce all email with a random"""\
              """ code\n                                   unavailable"""\
              """ - server always respondes with code 421\n"""\
              """                                     - service is"""\
              """ unavailable\n                                   """\
              """offline - server always responds with code 521 - """\
              """server\n                                     does not"""\
              """ accept mail\n\nWorkers\n-------\n\n  --workers=NUM"""\
              """                    Number of worker processes to"""\
              """ spawn.(default: # of CPUs/Cores - 2 + 1 master)\n\n"""
        print_help()
        self.assertEquals(stdout_mock.getvalue(), val)
