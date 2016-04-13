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

import argparse
import asyncore
import os
import socket
import sys

from blackhole.config import Config
from blackhole.smtp import SmtpHandler


class SmtpServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.config = Config()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            SmtpHandler(sock)


def config_test(args):
    conffile = args.config_file if args.config_file else None
    if conffile is None:
        print "No config file"
        sys.exit(os.EX_NOINPUT)
    Config(conffile).load().self_test()
    print "OK"
    sys.exit(os.EX_OK)


def run():
    parser = argparse.ArgumentParser('blackhole')
    parser.add_argument('-c', '--conf', help="Configuration file", type=str,
                        dest='config_file')
    parser.add_argument('-v', '--version', action='version',
                        version='2.0.1')
    parser.add_argument('-t', '--test', dest='test', action='store_true',
                        help="Perform a configuration test and exit")
    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help="Perform a configuration test and exit")
    args = parser.parse_args()
    if args.test:
        config_test(args)
    conffile = args.config_file if args.config_file else None
    config = Config(conffile).load().self_test()
    SmtpServer(config.address, config.port)
#    Server()
    asyncore.loop()
