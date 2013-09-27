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

"""
blackhole.application - Module is responsible for configuring, managing and
running the blackhole server instance and it's children.

It is the Python entry-point for the blackhole binary.
"""

import functools
import os
import signal

# ssl check
try:
    import ssl
except ImportError:
    ssl = None
import sys

# Bypass tornado.options to print custom version
# and help message
from blackhole import __fullname__
from blackhole.opts import print_help
for arg in sys.argv[1:]:
    if arg in ("--version", "-v"):
        print(__fullname__)
        sys.exit(0)
    if arg in ("--help", "-h"):
        print_help()
        sys.exit(0)

# set default options
from blackhole import opts

from deiman import Deiman
from tornado import (ioloop, process)
from tornado.options import options
options.parse_command_line()
if options.conf and os.path.exists(options.conf):
    options.parse_config_file(options.conf)

from blackhole.connection import (connection_ready, sockets)
from blackhole.log import log
from blackhole.ssl_utils import (BlackholeSSLException, verify_ssl_opts,
                                 sslkwargs)
from blackhole.utils import (setgid, setuid, terminate, set_process_title)


def set_action():
    """
    Figure out what action to perform based on arguments passed on the command
    line.

    start, stop or status
    """
    action = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            action = arg
    if action not in ('start', 'stop', 'status') or action is None:
        print_help()
        sys.exit(2)
    return action


def set_options():
    """
    Set our default options, overriding them as required i.e. for SSL.

    Also outputs warning message when using Debug and Delay modes and is
    responsible for warning about deprecated options.
    """
    # Deprecated options check
    opts.deprecated_opts()
    if options.debug:
        print("""WARNING: Using the debug flag!\n"""
              """This will generate a lots of disk I/O """
              """and large log files\n""")
    if options.delay > 0:
        print("""WARNING: Using the delay flag!\n"""
              """The delay flag is a blocking action """
              """and will cause connections to block.\n""")
    if options.ssl and not ssl:
        log.error("Unable to use SSL as SSL library is not compiled in")
        sys.exit(1)
    if options.ssl:
        try:
            verify_ssl_opts()
        except BlackholeSSLException as e:
            log.error(e)
            sys.exit(1)
        # Override SSL options based on options passed in
        sslkwargs['keyfile'] = options.ssl_key
        sslkwargs['certfile'] = options.ssl_cert


def daemon(action):
    """
    Trigger the daemon, run the action command and return the daemon object
    if required.

    'action' is a string, either start, stop or status
    Returns an instance of deiman.Deiman
    """
    d = Deiman(options.pid)
    if action == "stop":
        d.stop()
        sys.exit(0)
    elif action == "status":
        d.status()
        sys.exit(0)
    if len(sys.argv) == 1:
        print_help()
        sys.exit(2)
    if action == "start":
        d.start()
        return d
    else:
        sys.exit(0)


def fork():
    """
    Fork the processes off, set process titles (master, worker) and return
    and ioloop.

    Returns an instance of tornado.ioloop.IOLoop
    """
    # Set the custom process title of the master
    set_process_title()
     # Fork and create the ioloop
    options.workers = opts.workers()
    process.fork_processes(options.workers)
    io_loop = ioloop.IOLoop.instance()
    # Set the custom process title of the workers
    set_process_title()
    return io_loop


def run():
    """
    The run method is what actually spawns and manages blackhole.
    """
    signal.signal(signal.SIGTERM, terminate)
    action = set_action()
    set_options()
    # Grab the sockets early for multiprocessing
    if action in ('start',):
        socks = sockets()
        setgid()
        setuid()
    d = daemon(action)
    # Change group and user
    io_loop = fork()
    # Iterate over the dictionary of socket connections
    # and add them to the IOLoop
    for _, sock in socks.iteritems():
        callback = functools.partial(connection_ready, sock)
        io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
    try:
        io_loop.start()
    except (KeyboardInterrupt, SystemExit):
        io_loop.stop()
        d.stop()
        sys.exit(0)
