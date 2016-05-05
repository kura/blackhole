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


import logging
import signal
import os
import sys

from blackhole.config import (Config, config_test, parse_cmd_args,
                              _compare_uid_and_gid)
from blackhole.control import setgid, setuid
from blackhole.daemon import Daemon
from blackhole.exceptions import ConfigException, DaemonException
from blackhole.logs import configure_logs
from blackhole.supervisor import Supervisor


def run():
    """
    Create the asyncio loop and start the server.

    :raises: :any:`SystemExit` -- :any:`os.EX_USAGE` and :any:`os.EX_OK`
    """
    args = parse_cmd_args(sys.argv[1:])
    configure_logs(args)
    logger = logging.getLogger('blackhole')
    if args.test:
        config_test(args)
    try:
        config = Config(args.config_file).load().test()
        config.args = args
    except ConfigException as err:
        logger.fatal(err)
        raise SystemExit(os.EX_USAGE)
    if args.less_secure:
        logger.warn('Using -ls or --less-secure reduces security on '
                    'SSL/TLS connections')
    if not config.tls_dhparams and len(config.tls_listen) > 0:
        logger.warn('TLS is enabled but no Diffie Hellman ephemeral '
                    'parameters file was provided')
    _compare_uid_and_gid()
    try:
        daemon = Daemon(config.pidfile)
    except DaemonException as err:
        logger.fatal(err)
        raise SystemExit(os.EX_USAGE)
    supervisor = Supervisor()
    supervisor.create()
    setgid()
    setuid()
    signal.signal(signal.SIGTERM, supervisor.stop)
    signal.signal(signal.SIGINT, supervisor.stop)
    if args.background:
        try:
            daemon.daemonize()
        except DaemonException as err:
            supervisor.stop()
            logger.fatal(err)
            raise SystemExit(os.EX_USAGE)
    supervisor.run()
    raise SystemExit(os.EX_OK)
