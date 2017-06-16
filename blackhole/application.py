# (The MIT License)
#
# Copyright (c) 2013-2017 Kura
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

from .config import Config, config_test, parse_cmd_args, warn_options
from .control import pid_permissions, setgid, setuid
from .daemon import Daemon
from .exceptions import (BlackholeRuntimeException, ConfigException,
                         DaemonException)
from .logs import configure_logs
from .utils import blackhole_config_help
from .supervisor import Supervisor


__all__ = ('run', )
"""Tuple all the things."""


def blackhole_config():
    """
    Print the config help to the console with man-style formatting.

    :raises SystemExit: Exit code :py:obj:`os.EX_OK`.
    """
    args = parse_cmd_args(sys.argv[1:])
    configure_logs(args)
    logger = logging.getLogger('blackhole.blackhole_config')
    logger.info(blackhole_config_help)
    raise SystemExit(os.EX_OK)


def run():
    """
    Create the asyncio loop and start the server.

    :raises SystemExit: Exit code :py:obj:`os.EX_USAGE` when a configuration
                        error occurs, :py:obj:`os.EX_NOPERM` when a permission
                        error occurs or :py:obj:`os.EX_OK` when the program
                        exits cleanly.
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
