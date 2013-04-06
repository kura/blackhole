=========
Blackhole
=========

Blackhole is a `Tornado`_ powered MTA (mail transport agent) that is designed
for handling large volumes of email without handling any of the messages and
doing no disk bound I/O.

.. _Tornado: http://www.tornadoweb.org/

Blackhole is designed mostly for testing purposes and can be used to test
numerous things suchs as;

- Email send rates, if you need to test how much mail you can send per minute, hour etc
- Email integration testing and finally
- if you work in the real world, chances are you'll need work on a copy of production data from time to time. You can try to anonymous all the data but there is always a chance you'll miss something. Configuring blackhole as your applications default SMTP gateway will remove any chance of a real person receiving an email they shouldn't have received.

Using the blackhole.io service
==============================

All data sent to blackhole.io will be forgotten instantly, we store nothing you send.

1. Point your application's outgoing SMTP server to 'blackhole.io',
2. Sit back and watch mail never get delivered to a real user.

or, send an email to blackhole.io using an @blackhole.io address, any address is fine e.g.::

    user1@blackhole.io

Getting Started
===============

.. toctree::
    :maxdepth: 2

    installation
    configuration-options
    configuration-file-example
    controlling-the-server
    controlling-the-server-init-d
    modes
    response-codes

Reference
=========

.. toctree::
    :maxdepth: 2

    api-connection
    api-data
    api-log
    api-opts
    api-ssl-utils
    api-state
    api-utils

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
