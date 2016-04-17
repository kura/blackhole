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

"""
blackhole.application.

This module houses methods and functionality to start the server.
"""

import asyncio
import logging
import os
import sys

from blackhole.config import Config, config_test, parse_cmd_args
from blackhole.control import stop_servers, start_servers, setgid, setuid
from blackhole.daemon import Daemon
from blackhole.exceptions import ConfigException, DaemonException
from blackhole.logs import configure_logs


def run():
    """Create the asyncio loop and start the server."""
    args = parse_cmd_args()
    configure_logs(args)
    logger = logging.getLogger('blackhole')
    if args.test:
        config_test(args)
    conffile = args.config_file if args.config_file else None
    try:
        config = Config(conffile).load().self_test()
    except ConfigException as err:
        logger.fatal(err)
        sys.exit(os.EX_USAGE)
    if args.background and not config.pidfile:
        logger.fatal('Cannot run in background without a pidfile.')
        sys.exit(os.EX_USAGE)
    loop = asyncio.get_event_loop()
    start_servers()
    setgid()
    setuid()
    if args.background:
        try:
            Daemon(config.pidfile).daemonize()
        except DaemonException as err:
            stop_servers()
            logger.fatal(err)
            sys.exit(os.EX_USAGE)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    stop_servers()
