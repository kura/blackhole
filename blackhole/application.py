# (The MIT License)
#
# Copyright (c) 2016 Kura
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
import asyncio
import functools
import os
import socket
import sys

from blackhole.config import Config
from blackhole.smtp import Smtp

def config_test(args):
    # TODO: make less shitty
    conffile = args.config_file if args.config_file else None
    if conffile is None:
        print("No config file")
        sys.exit(os.EX_NOINPUT)
    Config(conffile).load().self_test()
    print("OK")
    sys.exit(os.EX_OK)


def run():
    # TODO: make less shitty
    parser = argparse.ArgumentParser('blackhole')
    parser.add_argument('-c', '--conf', help='Configuration file', type=str,
                        dest='config_file')
    parser.add_argument('-v', '--version', action='version',
                        version='2.0.1')
    parser.add_argument('-t', '--test', dest='test', action='store_true',
                        help='Perform a configuration test and exit')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help='Perform a configuration test and exit')
    args = parser.parse_args()
    if args.test:
        config_test(args)
    conffile = args.config_file if args.config_file else None
    config = Config(conffile).load().self_test()
    factory = functools.partial(Smtp)
    loop = asyncio.get_event_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    sock.bind((config.address, config.port))
    server = loop.run_until_complete(loop.create_server(factory, sock=sock))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
