===========================
:mod:`blackhole.connection`
===========================

.. module:: blackhole.connection
    :platform: Unix
    :synopsis: Connection
.. moduleauthor:: Kura <kura@kura.io>

Provide mechanisms for processing socket data.

This module provides methods for Blackhole to use internally
for binding and listening on sockets as well as process all
incoming socket data and responding appropriately.

blackhole.connection
====================

.. autofunction:: sockets()

.. autofunction:: connection_stream(connection)

.. autofunction:: ssl_connection(connection)

.. autofunction:: handle_command(line, mail_state)

.. autofunction:: connection_ready(sock, fd, events)

.. autofunction:: write_response(mail_state, resp)
