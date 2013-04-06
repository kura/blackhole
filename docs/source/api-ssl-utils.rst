==========================
:mod:`blackhole.ssl_utils`
==========================

.. module:: blackhole.ssl_utils
    :platform: Unix
    :synopsis: SSL Utils
.. moduleauthor:: Kura <kura@kura.io>

Utility functions for SSL wrapped sockets.

This module provides a simple default SSL configuration
for the blackhole server and also exposes a custom
'BlackholeSSLException' for SSL-based exceptions.

blackhole.ssl_utils
===================

.. autoexception:: BlackholeSSLException

.. autofunction:: verify_ssl_opts()