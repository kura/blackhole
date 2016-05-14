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

"""Provides functionality to run the server."""


import logging
import os
import sys

from .config import (Config, config_test, parse_cmd_args,
                     warn_options)
from .control import setgid, setuid, pid_permissions
from .daemon import Daemon
from .exceptions import (ConfigException, DaemonException,
                         BlackholeRuntimeException)
from .logs import configure_logs
from .supervisor import Supervisor


__all__ = ('run', )


def run():
    """
    Create the asyncio loop and start the server.

    :raises: :any:`SystemExit` -- :any:`os.EX_USAGE`, :any:`os.EX_OK` or
             :any:`os.EX_NOPERM`
    """
    args = parse_cmd_args(sys.argv[1:])
    configure_logs(args)
    logger = logging.getLogger('blackhole')
    if args.test:
        config_test(args)
    try:
        config = Config(args.config_file).load().test()
        config.args = args
        warn_options(config)
        daemon = Daemon(config.pidfile)
        supervisor = Supervisor()
        pid_permissions()
        setgid()
        setuid()
    except (ConfigException, DaemonException) as err:
        logger.fatal(err)
        raise SystemExit(os.EX_USAGE)
    except BlackholeRuntimeException as err:
        logger.fatal(err)
        raise SystemExit(os.EX_NOPERM)
    if args.background:
        try:
            daemon.daemonize()
        except DaemonException as err:
            supervisor.close_socks()
            logger.fatal(err)
            raise SystemExit(os.EX_NOPERM)
    try:
        supervisor.run()
    except KeyboardInterrupt:
        pass
    raise SystemExit(os.EX_OK)
