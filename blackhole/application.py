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

This module houses methods and functionality to start the blackhole server.
"""

import argparse
import asyncio
import functools
import logging
from logging.config import dictConfig
import os
import socket
import ssl
import sys

from blackhole.config import Config
from blackhole.exceptions import ConfigException
from blackhole.smtp import Smtp


version = __import__('blackhole').__version__

debug_format = '[%(levelname)s] blackhole.%(module)s: %(message)s'
log_config = {
    'version': 1,
    'formatters': {
        'console': {'format': '%(message)s'},
        'debug': {'format': debug_format}
    },
    'handlers': {
    },
    'loggers': {
        'blackhole': {'handlers': [], 'level': logging.WARN},
    }
}

debug_handler = {'class': 'logging.StreamHandler',
                 'formatter': 'debug', 'level': logging.DEBUG}
default_handler = {'class': 'logging.StreamHandler',
                   'formatter': 'console', 'level': logging.INFO}


def config_test(args):
    """
    Test the validity of the configuration file content.

    .. note::

       Problems with the configuration will be written to the console using
       the `logging` module.

       Calls `sys.exit` upon an error.

    :param args: arguments parsed from `argparse`.
    :type args: `argparse.Namespace`
    """
    conffile = args.config_file if args.config_file else None
    logger = logging.getLogger('blackhole.config_test')
    logger.setLevel(logging.INFO)
    if conffile is None:
        logger.fatal('No config file provided.')
        sys.exit(os.EX_USAGE)
    Config(conffile).load().self_test()
    logger.info('%s syntax is OK', conffile)
    logger.info('%s test was successful', conffile)
    sys.exit(os.EX_OK)


def create_server(use_tls=False):
    """
    Create an instance of `socket.socket`, binds it and attaches it to loop.

    .. note::

       Calls `sys.exit` when there is an error binding to the socket.
       If `use_tls` is passed, the SSL/TLS context will be created with
       `ssl.OP_NO_SSLv2` and `ssl.OP_NO_SSLv3`.

    :param use_tls: default False.
    :type use_tls: bool
    :returns: generator
    """
    logger = logging.getLogger('blackhole')
    config = Config()
    port = config.tls_port if use_tls else config.port
    if use_tls:
        logger.debug('Creating server (%s, %s, TLS=True)', config.address,
                     port)
    else:
        logger.debug('Creating server (%s, %s)', config.address, port)
    loop = asyncio.get_event_loop()
    factory = functools.partial(Smtp)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    try:
        sock.bind((config.address, port))
    except socket.error:
        logger.fatal("Cannot bind to port %s.", port)
        sys.exit(os.EX_NOPERM)
    if use_tls:
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.load_cert_chain(config.tls_cert, config.tls_key)
        ctx.options &= ~ssl.OP_NO_SSLv2
        ctx.options &= ~ssl.OP_NO_SSLv3
    else:
        ctx = None
    return loop.create_server(factory, sock=sock, ssl=ctx)


def run():
    """
    Create the asyncio loop and start the blackhole server.

    .. note::

       Calls `sys.exit` upon a configuration error.
       Configures the `logging` module.
    """
    # TODO: make less shitty
    parser = argparse.ArgumentParser('blackhole')
    parser.add_argument('-c', '--conf', type=str,
                        dest='config_file', metavar='/etc/blackhole.conf')
    parser.add_argument('-v', '--version', action='version',
                        version=version)
    parser.add_argument('-t', '--test', dest='test', action='store_true',
                        help='perform a configuration test and exit')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help='enable debugging mode.')
    args = parser.parse_args()
    logger = logging.getLogger('blackhole')
    logger_handlers = log_config['loggers']['blackhole']['handlers']
    if args.debug and not args.test:
        log_config['handlers']['debug_handler'] = debug_handler
        logger_handlers.append('debug_handler')
    else:
        log_config['handlers']['default_handler'] = default_handler
        logger_handlers.append('default_handler')
    dictConfig(log_config)
    if args.test:
        config_test(args)
    conffile = args.config_file if args.config_file else None
    try:
        config = Config(conffile).load().self_test()
    except ConfigException as err:
        logger.fatal(err)
        sys.exit(os.EX_USAGE)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_server())
    if config.tls_port and config.tls_cert and config.tls_key:
        loop.run_until_complete(create_server(True))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
