=============================================
Blackhole |pypi| |travis| |coverage| |gitter|
=============================================

Blackhole is an `MTA (message transfer agent)
<https://en.wikipedia.org/wiki/Message_transfer_agent>`_ that (figuratively)
pipes all mail to /dev/null.

Blackhole is built on top of `asyncio
<https://docs.python.org/3/library/asyncio.html>`_ and utilises `async def <https://docs.python.org/3/reference/compound_stmts.html#async-def>`_
and `await <https://docs.python.org/3/reference/expressions.html#await>`_
statements available in `Python 3.5
<https://docs.python.org/3/whatsnew/3.5.html>`_ and above and the `pathlib
<https://docs.python.org/3/library/pathlib.html#module-pathlib>`_ module made
available by Python 3.6.

While blackhole is an MTA (mail transport agent), none of the actions
performed via SMTP or SMTPS are actually processed and no email or sent or
delivered.

You can tell blackhole how to handle mail that it receives. It can accept all
of it, bounce it all or randomly do either of those two actions. No matter how
you choose to configure it, the email is never actually delivered, it just
appears to have been delivered or bounced.

Think of blackhole sort of like a honeypot in terms of how it handles mail,
but it's specifically designed with testing in mind.

Donations
=========

Blackhole costs a bit of money to run, it receives millions of emails on a
daily basis, sometimes millions every 5 minutes depending on the load of the
platform.

To keep Blackhole running, please think about donating even just a little to
the project `via Gratipay <https://gratipay.com/blackhole.io/>`_.

Why?
====

Blackhole was first built when I was working on a project that required me to
be able to send/receive millions of emails per minute. As the sender was being
prototyped, I quickly realised that any mail server I pointed it at would fall
over due to the stess -- thus blackhole was born.


Communicating with the SMTP service
===================================

Supported commands/verbs and dynamic responses
----------------------------------------------

You can find a list of all supported commands/verbs and their parameters in
the :ref:`commands` section.

Some commands allow you to define how they respond. For instance, telling an
``AUTH`` command to fail authentication.

You can find a full list of commands/verbs who's behaviour can be modified
on-the-fly, including how they can be modified and what values they will return
in the :ref:`dynamic-responses` section.


.. _help-verb:

HELP command/verb
-----------------

Blackhole has support for the ``HELP`` verb, allowing you to quickly and easily
see which commands are and are not implemented. You can use this command verb
as described below.

.. code-block:: none

    >>> HELP
    250 Supported commands: DATA EHLO ETRN HELO...
    >>> HELP HELO
    250 Syntax: HELO domain.tld
    >>> HELO kura.io
    250 OK
    >>> HELP INVALID
    501 Supported commands: DATA EHLO ETRN HELO...

By design, the blackhole server doesn't care about the order you send commands,
whether they are capitalised or whether you send a valid, fully qualified
domain name or valid from and to email addresses.


Dynamic delay and response mode switches
----------------------------------------

Blackhole allows you to configure an amount of time to wait before responding
to a client and how to respond, for example accept the mail or bounce it.

You can also configure these settings on-the-fly per email, using headers.

Please read the :ref:`dynamic-switches` section for more information on dynamic
switches.


SSL/TLS configuration
---------------------

The blackhole codebase is designed with these `security considerations <https://docs.python.org/3/library/ssl.html#ssl-security>`_ in
mind. As such, `SSLv2` and `SSLv3` are explicitly disabled and these ciphers
are used.

.. code-block:: none

    0xC0,0x2C  -  ECDHE-ECDSA-AES256-GCM-SHA384  TLSv1.2  Kx=ECDH  Au=ECDSA  Enc=AESGCM(256)    Mac=AEAD
    0xC0,0x30  -  ECDHE-RSA-AES256-GCM-SHA384    TLSv1.2  Kx=ECDH  Au=RSA    Enc=AESGCM(256)    Mac=AEAD
    0xCC,0x14  -  ECDHE-ECDSA-CHACHA20-POLY1305  TLSv1.2  Kx=ECDH  Au=ECDSA  Enc=ChaCha20(256)  Mac=AEAD
    0xCC,0x13  -  ECDHE-RSA-CHACHA20-POLY1305    TLSv1.2  Kx=ECDH  Au=RSA    Enc=ChaCha20(256)  Mac=AEAD
    0xC0,0x2B  -  ECDHE-ECDSA-AES128-GCM-SHA256  TLSv1.2  Kx=ECDH  Au=ECDSA  Enc=AESGCM(128)    Mac=AEAD
    0xC0,0x2F  -  ECDHE-RSA-AES128-GCM-SHA256    TLSv1.2  Kx=ECDH  Au=RSA    Enc=AESGCM(128)    Mac=AEAD
    0xC0,0x24  -  ECDHE-ECDSA-AES256-SHA384      TLSv1.2  Kx=ECDH  Au=ECDSA  Enc=AES(256)       Mac=SHA384
    0xC0,0x28  -  ECDHE-RSA-AES256-SHA384        TLSv1.2  Kx=ECDH  Au=RSA    Enc=AES(256)       Mac=SHA384
    0xC0,0x23  -  ECDHE-ECDSA-AES128-SHA256      TLSv1.2  Kx=ECDH  Au=ECDSA  Enc=AES(128)       Mac=SHA256
    0xC0,0x27  -  ECDHE-RSA-AES128-SHA256        TLSv1.2  Kx=ECDH  Au=RSA    Enc=AES(128)       Mac=SHA256

These ciphers are specifically taken from `modern` configuration on the
`Mozilla TLS page <https://wiki.mozilla.org/Security/Server_Side_TLS>`_. The
code that handles wrapping SSL/TLS sockets, can be found `on GitHub <https://github.com/kura/blackhole/blob/master/blackhole/control.py#L89-L93>`_.

You can test the default security using `testssl.sh <https://testssl.sh/>`_.

.. code-block:: bash

    testssl.sh blackhole.io 465

Example output of `testssl.sh` testing the blackhole server can be found
`here </testssl.sh.html>`_.


STARTTLS
--------

Currently `asyncio` does not have the code in place to make STARTTLS
possible, the STARTTLS verb returns a ``500 Not implemented`` response
until it's possible to implement. --`https://bugs.python.org/review/23749/
<https://bugs.python.org/review/23749/>`_

While STARTTLS is disabled, you can still talk to blackhole over SMTPS on
it's standard port ``465`` as well as unencrypted, on the standard ports ``25``
and ``587``.

MX
--

This service provides real MX records, allowing any `@blackhole.io` to appear
as if it works. Blackhole will accept any email from or to any domain.

.. code::

    blackhole.io.    IN MX    10 blackhole.io.

To try this, fire up your email client and send an email to
`random@blackhole.io`. This email will appear to have been sent and
received with no issue. That's because it has, it just never actually gets
delivered to anyone.


SMTP & SMTPS in code
--------------------

This service can be configured as an SMTP server for an application. Any mail
the application tries to send will hit the blackhole.io service and look as if
it was sent and received, but no actually email is sent out.

.. code-block:: python

    # from smtplib import SMTP             # For sending without SSL/TLS.
    from smtplib import SMTP_SSL

    msg = '''From: <test@blackhole.io>
    To: <test@blackhole.io>
    Subject: Test email

    Random test email. Some UTF-8 characters: ßæøþ'''

    # smtp = SMTP('blackhole.io', 25)      # For sending without SSL/TLS.
    smtp = SMTP_SSL('blackhole.io', 465)
    smtp.sendmail('test@blackhole.io', 'test@blackhole.io',
                  msg.encode('utf-8'))

    # We can send multiple messages using the same connection.
    smtp.sendmail('tset@blackhole.io', 'tset@blackhole.io',
                  msg.encode('utf-8'))

    # Quit after we're done
    smtp.quit()

This example is written in Python but, any language can be used to communicate
with the blackhole server. Blackhole is capable of receiving non-ASCII
characters.


.. _telnet:

Testing with telnet
-------------------

::

    Trying 46.101.237.170...
    Connected to blackhole.io.
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

You can talk to the SSL/TLS endpoint using ``openssl s_client``.


Running your own server
=======================

For those of you that want to run your own copy of this service, the
:ref:`running-your-own-server` document should have all of the information
you'll need, and a little more.


Running the test framework
==========================

Please see the :ref:`testing` section for information on how to run the unit
tests against the source code.


Contributing
============

Please see the :ref:`contributing` section for information on how to
contribute. The :ref:`api` section also has a wealth of information on how
the server works and how you can modify it or use parts of it.


Upcoming/planned features
=========================

There is a list of upcoming/planned features on the :ref:`todo` page.

Two of the biggest upcoming features will be
`POP3 <https://en.wikipedia.org/wiki/Post_Office_Protocol>`_ and
`IMAP4 <https://en.wikipedia.org/wiki/Internet_Message_Access_Protocol>`_
support, to help with email client development, tesing and whatever else you
want to use it for.

If you have a feature you need or would like, feel free to put an issue on the
`issue tracker <https://github.com/kura/blackhole/issues>`_ or take a look at
the :ref:`contributing` section for information on how you could implement
the functionality yourself.


License
=======

Blackhole is licensed under the `MIT license <https://github.com/kura/blackhole/blob/master/LICENSE>`_.


Changelog
=========

.. toctree::
    :maxdepth: 3

    changelog


Frequently asked questions
==========================

You can find a list of questions and answers in the
:ref:`frequently-asked-questions` section.


API documentation
=================

.. toctree::
   :maxdepth: 2

   api-application
   api-child
   api-config
   api-control
   api-daemon
   api-exceptions
   api-logs
   api-protocols
   api-smtp
   api-streams
   api-supervisor
   api-utils
   api-worker


Author
======

Written and maintained by `Kura <https://kura.io/>`_. You can stalk Kura on
`Twitter <https://twitter.com/kuramanga>`_ and laugh at his code on `GitHub
<https://github.com/kura>`_.


Thanks & contributors
=====================

Thanks are here -- :ref:`thanks` and contributors here -- :ref:`contributors`.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. |pypi| image:: https://img.shields.io/pypi/v/blackhole.svg?style=flat-square&label=version
    :target: https://pypi.python.org/pypi/blackhole
    :alt: Latest version released on PyPi

.. |travis| image:: https://img.shields.io/travis/kura/blackhole/master.svg?style=flat-square&label=build
    :target: http://travis-ci.org/kura/blackhole
    :alt: Build status of the master branch

.. |coverage| image:: https://img.shields.io/codecov/c/github/kura/blackhole/master.svg?style=flat-square&label=coverage
    :target: https://codecov.io/github/kura/blackhole/
    :alt: Test coverage

.. |gitter| image:: https://img.shields.io/gitter/room/kura/blackhole.svg?style=flat-square
    :target: https://gitter.im/kura/blackhole
    :alt: Chat on Gitter
