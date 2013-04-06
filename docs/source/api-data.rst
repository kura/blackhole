=====================
:mod:`blackhole.data`
=====================

.. module:: blackhole.data
    :platform: Unix
    :synopsis: Data
.. moduleauthor:: Kura <kura@kura.io>

Provides SMTP response codes and methods
for returning the correct response code.

This module contains all usable SMTP response codes for
returning through the socket.
It also provides mechanisms for picking response codes
that mean a mail message has been accepted, rejected or
that the server is offline.

blackhole.data
====================

.. autofunction:: response(response)

.. autofunction:: get_response()

.. autofunction:: random_choice(response_list)

.. autofunction:: response_message(response)