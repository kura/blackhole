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

"""Provides control functionality, including socket wrappers."""

import grp
import logging
import os
import pwd
import socket
try:
    import ssl
except ImportError:
    ssl = None

from .config import Config
from .exceptions import BlackholeRuntimeException


__all__ = ('pid_permissions', 'server', 'setgid', 'setuid')


logger = logging.getLogger('blackhole.control')
ciphers = ['ECDHE-ECDSA-AES256-GCM-SHA384', 'ECDHE-RSA-AES256-GCM-SHA384',
           'ECDHE-ECDSA-CHACHA20-POLY1305', 'ECDHE-RSA-CHACHA20-POLY1305',
           'ECDHE-ECDSA-AES128-GCM-SHA256', 'ECDHE-RSA-AES128-GCM-SHA256',
           'ECDHE-ECDSA-AES256-SHA384', 'ECDHE-RSA-AES256-SHA384',
           'ECDHE-ECDSA-AES128-SHA256', 'ECDHE-RSA-AES128-SHA256']


def _context(use_tls=False):
    """
    Create a TLS context using the certificate, key and dhparams file.

    :param use_tls: Whether to create a TLS context or not.
    :type use_tls: :any:`bool`
    :returns: A TLS context or none.
    :rtype: :any:`ssl.SSLContext` or :any:`None`.

    .. note::

       Created with:

       - :any:`ssl.OP_NO_SSLv2`
       - :any:`ssl.OP_NO_SSLv3`
       - :any:`ssl.OP_NO_COMPRESSION`
       - :any:`ssl.OP_CIPHER_SERVER_PREFERENCE`

       Also responsible for loading Diffie Hellman ephemeral parameters if
       they're provided -- :any:`ssl.SSLContext.load_dh_params`

       If the ``-ls`` or ``--less-secure`` option is provided,
       :any:`ssl.OP_SINGLE_DH_USE` and :any:`ssl.OP_SINGLE_ECDH_USE` will be
       omitted from the context. --
       https://blackhole.io/command-line-options.html#command-line-options --
       added in :ref:`2.0.13`
    """
    if use_tls is False:
        return None
    config = Config()
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(config.tls_cert, config.tls_key)
    ctx.options |= ssl.OP_NO_SSLv2
    ctx.options |= ssl.OP_NO_SSLv3
    ctx.options |= ssl.OP_NO_COMPRESSION
    ctx.options |= ssl.OP_CIPHER_SERVER_PREFERENCE
    if not config.args.less_secure:
        ctx.options |= ssl.OP_SINGLE_DH_USE
        ctx.options |= ssl.OP_SINGLE_ECDH_USE
    ctx.set_ciphers(':'.join(ciphers))
    if config.tls_dhparams:
        ctx.load_dh_params(config.tls_dhparams)
    return ctx


def _socket(addr, port, family):
    """
    Create a socket, bind and listen.

    :param addr: The address to use.
    :type addr: :any:`str`
    :param port: The port to use.
    :type port: :any:`int`
    :param family: The type of socket to use.
    :type family: :any:`socket.AF_INET` or :any:`socket.AF_INET6`.
    :returns: A bound socket.
    :rtype: :any:`socket.socket`
    :raises: :any:`blackhole.exceptions.BlackholeRuntimeException`
    """
    sock = socket.socket(family, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except (AttributeError, OSError):
        pass
    if family == socket.AF_INET6:
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
    try:
        sock.bind((addr, port))
    except OSError:
        msg = 'Cannot bind to {}:{}.'.format(addr, port)
        logger.fatal(msg)
        sock.close()
        raise BlackholeRuntimeException(msg)
    os.set_inheritable(sock.fileno(), True)
    sock.listen(1024)
    sock.setblocking(False)
    return sock


def server(addr, port, family, flags={}, use_tls=False):
    """
    A socket and possibly a TLS context.

    Create an instance of :any:`socket.socket`, bind it and return a dictionary
    containing the socket object and a TLS context if configured.

    :param addr: The address to use.
    :type addr: :any:`str`
    :param port: The port to use.
    :type port: :any:`int`
    :param family: The type of socket to use.
    :type family: :any:`socket.AF_INET` or :any:`socket.AF_INET6`.
    :param flags: Flags to use.
    :type flags: :any:`dict`. Default: {}
    :param use_tls: Whether to create a TLS context or not.
    :type use_tls: :any:`bool`
    :returns: A bound socket, a TLS context if configured and any configured
              flags.
    :rtype: :any:`dict`
    """
    sock = _socket(addr, port, family)
    ctx = _context(use_tls=use_tls)
    return {'sock': sock, 'ssl': ctx, 'flags': flags}


def pid_permissions():
    """
    Change the pid file ownership.

    Called before :any:`blackhole.control.setgid` and
    :any:`blackhole.control.setuid` are called to stop
    :any:`blackhole.daemon.Daemon` losing permissions to modify the pid file.

    :raises: :any:`SystemExit` -- :any:`os.EX_USAGE`
    """
    config = Config()
    try:
        user = pwd.getpwnam(config.user)
        group = grp.getgrnam(config.group)
        os.chown(config.pidfile, user.pw_uid, group.gr_gid)
    except (KeyError, PermissionError):
        logger.error('Unable to change pidfile ownership permissions.')
        raise SystemExit(os.EX_USAGE)


def setgid():
    """
    Change group.

    Change to a less privileged group. Unless you're using it incorrectly --
    in which case, don't use it.
    :raises: :any:`SystemExit` -- :any:`os.EX_USAGE` or :any:`os.EX_NOPERM`

    .. note::

       MUST be called BEFORE setuid, not after.
    """
    config = Config()
    try:
        gid = grp.getgrnam(config.group).gr_gid
        os.setgid(gid)
    except KeyError:
        logger.error('Group \'%s\' does not exist.', config.group)
        raise SystemExit(os.EX_USAGE)
    except PermissionError:
        logger.error('You do not have permission to switch to group \'%s\'.',
                     config.group)
        raise SystemExit(os.EX_NOPERM)


def setuid():
    """
    Change user.

    Change to a less privileged user.Unless you're using it incorrectly --
    inwhich case, don't use it.
    :raises: :any:`SystemExit` -- :any:`os.EX_USAGE` or :any:`os.EX_NOPERM`

    .. note::

       MUST be called AFTER setgid, not before.
    """
    config = Config()
    try:
        uid = pwd.getpwnam(config.user).pw_uid
        os.setuid(uid)
    except KeyError:
        logger.error('User \'%s\' does not exist.', config.user)
        raise SystemExit(os.EX_USAGE)
    except PermissionError:
        logger.error('You do not have permission to switch to user \'%s\'.',
                     config.user)
        raise SystemExit(os.EX_NOPERM)
