import os
import ssl

from tornado.options import options

from blackhole.log import log


sslkwargs = {
    'do_handshake_on_connect': False,
    'server_side': True,
    'ssl_version': ssl.PROTOCOL_TLSv1,
    'keyfile': options.ssl_key,
    'certfile': options.ssl_cert,
    'ca_certs': options.ssl_ca_certs_dir,
    'ciphers': None,
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
        raise BlackholeSSLException("You need to set an SSL certificate and SSL key")
    if not os.path.exists(options.ssl_cert):
        raise BlackholeSSLException("Certificate '%s' does not exist" % options.ssl_cert)
    if options.ssl_key and not os.path.exists(options.ssl_key):
        raise BlackholeSSLException("Keyfile '%s' does not exist" % options.ssl_key)
