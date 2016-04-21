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
blackhole.control.

Command and control functionality for blackhole.
"""

import asyncio
import functools
import getpass
import grp
import logging
import os
import pwd
import socket
try:
    import ssl
except ImportError:
    ssl = None
from blackhole.config import Config
from blackhole.daemon import Daemon
from blackhole.smtp import Smtp


logger = logging.getLogger('blackhole.control')
_servers = []
ciphers = ['ECDHE-ECDSA-AES256-GCM-SHA384', 'ECDHE-RSA-AES256-GCM-SHA384',
           'ECDHE-ECDSA-CHACHA20-POLY1305', 'ECDHE-RSA-CHACHA20-POLY1305',
           'CDHE-ECDSA-AES128-GCM-SHA256', 'ECDHE-RSA-AES128-GCM-SHA256:',
           'ECDHE-ECDSA-AES256-SHA384', 'ECDHE-RSA-AES256-SHA384'
           'ECDHE-ECDSA-AES128-SHA256', 'ECDHE-RSA-AES128-SHA256']


def create_server(use_tls=False):
    """
    Create an instance of `socket.socket`, bind it and attach it to loop.

    .. note::

       Calls `sys.exit` when there is an error binding to the socket.
       If `use_tls` is passed, the SSL/TLS context will be created with
       `ssl.OP_NO_SSLv2` and `ssl.OP_NO_SSLv3`.

    :param use_tls: default False.
    :type use_tls: bool
    """
    logger = logging.getLogger('blackhole')
    config = Config()
    port = config.tls_port if use_tls else config.port
    if use_tls:
        logger.debug('Creating server (%s, %s, TLS=True)', config.address,
                     port)
        if ssl is None:
            logger.debug('TLS is disabled, skipping.')
            return
    else:
        logger.debug('Creating server (%s, %s)', config.address, port)
    loop = asyncio.get_event_loop()
    factory = functools.partial(Smtp)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    try:
        sock.bind((config.address, port))
    except OSError:
        logger.fatal("Cannot bind to port %s.", port)
        raise SystemExit(os.EX_NOPERM)
    if use_tls:
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.load_cert_chain(config.tls_cert, config.tls_key)
        ctx.options |= ssl.OP_NO_SSLv2
        ctx.options |= ssl.OP_NO_SSLv3
        ctx.set_ciphers(':'.join(ciphers))
    else:
        ctx = None
    server = loop.create_server(factory, sock=sock, ssl=ctx)
    _servers.append(loop.run_until_complete(server))


def start_servers():
    """Create each server listener and bind to the socket."""
    config = Config()
    logger.debug('Starting...')
    create_server()
    if config.tls_port and config.tls_cert and config.tls_key:
        if ssl is not None:
            create_server(use_tls=True)
        else:
            logger.debug('TLS is disabled, skipping.')
            return

def stop_servers():
    """
    Stop the listeners.

    :raises: SystemExit
    """
    loop = asyncio.get_event_loop()
    conf = Config()
    logger.debug('Stopping...')
    for _ in range(len(_servers)):
        server = _servers.pop()
        server.close()
        loop.run_until_complete(server.wait_closed())
    loop.close()
    daemon = Daemon(conf.pidfile)
    if daemon.pid:
        del daemon.pid


def setgid():
    """
    Change group.

    Drop from root privileges down to a less privileged group.

    .. note::

       MUST be called BEFORE setuid, not after.
    """
    config = Config()
    if config.group == grp.getgrgid(os.getgid()).gr_name:
        logger.debug('Group in config is the same as current group, skipping.')
        return
    try:
        os.setgid(grp.getgrnam(config.group).gr_gid)
    except KeyError:
        logger.error("Group '%s' does not exist", config.group)
        raise SystemExit(os.EX_USAGE)
    except PermissionError:
        logger.error("You do not have permission to switch to group '%s'",
                     config.group)
        raise SystemExit(os.EX_NOPERM)


def setuid():
    """
    Change user.

    Drop from root privileges down to a less privileged user.

    .. note::

       MUST be called AFTER setgid, not before.
    """
    config = Config()
    if config.user == getpass.getuser():
        logger.debug('User in config is the same as current user, skipping.')
        return
    try:
        os.setuid(pwd.getpwnam(config.user).pw_uid)
    except KeyError:
        logger.error("User '%s' does not exist", config.user)
        raise SystemExit(os.EX_USAGE)
    except PermissionError:
        logger.error("You do not have permission to switch to user '%s'",
                     config.user)
        raise SystemExit(os.EX_NOPERM)
