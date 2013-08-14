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
blackhole.ssl_utils - Utility functions for SSL
wrapped sockets.

This module provides a simple default SSL configuration
for the blackhole server and also exposes a custom
'BlackholeSSLException' for SSL-based exceptions.
"""

import os
import ssl

from tornado.options import options


sslkwargs = {
    'do_handshake_on_connect': False,
    'server_side': True,
    'ssl_version': ssl.PROTOCOL_SSLv3,
    'keyfile': options.ssl_key,
    'certfile': options.ssl_cert,
}


class BlackholeSSLException(Exception):
    """A simple Exception class"""
    pass


def verify_ssl_opts():
    """
    Verify our SSL configuration variables are
    correctly set-up.
    """
    if not options.ssl_key or not options.ssl_cert:
        raise BlackholeSSLException("""You need to set an SSL certificate"""
                                    """ and SSL key""")
    if not os.path.exists(options.ssl_cert):
        raise BlackholeSSLException("Certificate '%s' does not exist" %
                                    options.ssl_cert)
    if options.ssl_key and not os.path.exists(options.ssl_key):
        raise BlackholeSSLException("Keyfile '%s' does not exist" %
                                    options.ssl_key)
    return True
