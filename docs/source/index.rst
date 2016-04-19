=========
Blackhole
=========


About
=====

Blackhole is an email MTA that (figuratively) pipes all mail to /dev/null.

Blackhole is built on top of `asyncio <https://docs.python.org/3/library/asyncio.html>`_
and utilises `async def <https://docs.python.org/3/reference/compound_stmts.html#async-def>`_
and `await <https://docs.python.org/3/reference/expressions.html#await>`_
statements available in Python 3.5 and above.

While Blackhole is an MTA (mail transport agent), none of the actions
performed via SMTP or SMTPS are actually processed and no email or sent or
delivered.

You can tell Blackhole how to handle mail that it receives. It can accept all
of it, bounce it all or randomly do either of those two actions. No matter how
you choose to configure it, the email is never actually delivered, it just
appears to have been delivered or bounced.

Think of Blackhole sort of like a honeypot in terms of how it handles mail,
but it's specifically designed with testing in mind.


Python < 3.5
------------

The original incarnation of Blackhole -- built on top of Tornado -- is still
available for use on Python versions lower than 3.5, including PyPy.

It is no longer maintained however, but is available for posterity's sake on
`PyPI <https://pypi.python.org/pypi/blackhole>`_ and `GitHub
<https://github.com/kura/blackhole/>`_.


-----

|pypi| |travis| |coverage| |gitter|

-----


Why?
====

Blackhole was first built when I was working on a project that required me to
be able to send/receive millions of emails per minute. As the sender was being
prototyped, I quickly realised that any mail server I pointed it at would fall
over due to the stess -- thus blackhole was born.


Getting started
===============

.. toctree::
    :maxdepth: 2

    running-your-own-server
    command-line-options
    configuration-file-example
    delay-flag
    controlling-the-server-with-init-d
    modes
    response-codes
    contributing
    changelog
    todo


Using the blackhole.io service
==============================

STARTTLS
--------

Currently `asyncio` does not have the code in place to make *STARTTLS*
possible, the *STARTTLS* verb returns a ``500 Not implemented`` response
until it's possible to implement. -- `https://bugs.python.org/review/23749/ <https://bugs.python.org/review/23749/>`_

While *STARTTLS* is disabled, you can still talk to blackhole over SMTPS on
it's standard port 465 as well as unencrypted, on the standard port 25.

MX
--

This service provides real MX records, allowing any `@blackhole.io` to appear as
if it works.

.. code::

    blackhole.io.    IN MX    10 blackhole.io.

To try this, fire up your email client and send an email to
`random@blackhole.io`. This email will appear to have been sent and
received with no issue. That's because it has, it just never actually gets
delivered to anyone.


Via SMTP and SMTPS
------------------

This service can be configured as an SMTP server for an application. Any mail
the application tries to send will hit the blackhole.io service and look as if
it was sent and received, but no actually email is sent out.

.. code-block:: python
   :linenos:

    from smtplib import SMTP

    msg = """From: <test@blackhole.io>
    To: <test@blackhole.io>
    Subject: Test

    Random test message.
    """

    smtp = SMTP('blackhole.io', 25)
    smtp.sendmail('test@blackhole.io', 'test@blackhole.io',
                  msg.encode('utf-8'))
    smtp.quit()


Test via telnet
---------------

::

    Trying 127.0.0.1...
    Connected to localhost.
    Escape character is '^]'.
    220 blackhole.io ESMTP
    EHLO blackhole.io
    250-blackhole.io
    250-PIPELINING
    250-SIZE 512000
    250-VRFY
    250-ETRN
    250-ENHANCEDSTATUSCODES
    250-8BITMIME
    250 DSN
    MAIL FROM: <test@blackhole.io>
    250 2.1.0 OK
    RCPT TO: <test@blackhole.io>
    250 2.1.5 OK
    DATA
    354 End data with <CR><LF>.<CR><LF>
    To: <test@blackhole.io>
    From: <test@blackhole.io>
    Subject: Test

    Random test message.
    .
    250 2.0.0 OK: queued as <20160418202241.7778.853458045.0@blackhole.io>
    QUIT
    221 2.0.0 Goodbye
    Connection closed by foreign host.



Running the source code unit tests
==================================

Please see the :ref:`testing` section for information on how to run the unit
tests against the source code.


Contributing
============

Please see the :ref:`contributing` section for information on how to
contribute.

Author
======

Written and maintained by `Kura <https://kura.io/>`_.


Changelog
=========

.. toctree::
    :maxdepth: 2

    changelog


Reference
=========

.. toctree::
    :maxdepth: 2

    api-application
    api-config
    api-control
    api-daemon
    api-exceptions
    api-logs
    api-smtp
    api-utils

Thanks & contributors
=====================

Thanks are here - :ref:`thanks` and contributors here :ref:`contributors`.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. |pypi| image:: https://img.shields.io/pypi/v/blackhole.svg?style=flat-square&label=version
    :target: https://pypi.python.org/pypi/blackhole
    :alt: Latest version released on PyPi

.. |coverage| image:: https://img.shields.io/codecov/c/github/kura/blackhole/master.svg?style=flat-square&label=coverage
    :target: https://codecov.io/github/kura/blackhole/
    :alt: Test coverage

.. |travis| image:: https://img.shields.io/travis/kura/blackhole/master.svg?style=flat-square&label=build
    :target: http://travis-ci.org/kura/blackhole
    :alt: Build status of the master branch

.. |gitter| image:: https://img.shields.io/gitter/room/kura/blackhole.svg?style=flat-square
    :target: https://gitter.im/kura/blackhole
    :alt: Chat on Gitter
