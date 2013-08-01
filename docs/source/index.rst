=========
Blackhole
=========

::

     .o8       oooo                      oooo        oooo                  oooo                 o8o
    "888       `888                      `888        `888                  `888                 `"'
     888oooo.   888   .oooo.    .ooooo.   888  oooo   888 .oo.    .ooooo.   888   .ooooo.      oooo   .ooooo.
     d88' `88b  888  `P  )88b  d88' `"Y8  888 .8P'    888P"Y88b  d88' `88b  888  d88' `88b     `888  d88' `88b
     888   888  888   .oP"888  888        888888.     888   888  888   888  888  888ooo888      888  888   888
     888   888  888  d8(  888  888   .o8  888 `88b.   888   888  888   888  888  888    .o .o.  888  888   888
     `Y8bod8P' o888o `Y888""8o `Y8bod8P' o888o o888o o888o o888o `Y8bod8P' o888o `Y8bod8P' Y8P o888o `Y8bod8P'

.. image:: https://api.travis-ci.org/kura/blackhole.png?branch=master
        :target: https://travis-ci.org/kura/blackhole

.. image:: https://coveralls.io/repos/kura/blackhole/badge.png?branch=master
        :target: https://coveralls.io/r/kura/blackhole

.. image:: https://pypip.in/d/blackhole/badge.png
        :target: https://crate.io/packages/blackhole

.. image:: https://pypip.in/v/blackhole/badge.png
        :target: https://crate.io/packages/blackhole

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

Testing via telnet
------------------

::

    $ telnet blackhole 25
    Trying 198.199.126.159...
    Connected to blackhole.io.
    Escape character is '^]'.
    220 blackhole.io [blackhole 1.7.0 (Stable)]
    HELO fake.mail.server
    250 OK
    MAIL FROM:<user@address.tld>
    250 OK
    RCPT TO:<someone@another.tld>
    250 OK
    DATA
    354 Start mail input; end with <CRLF>.<CRLF>
    To: Someone <someone@another.tld>
    From: User <user@address.tld>
    Subject: Bye

    Bye bye email
    .
    250 OK
    QUIT
    221 Thank you for speaking to me
    Connection closed by foreign host.

Testing SSL
-----------

::

    $ openssl s_client -connect blackhole.io:465
    CONNECTED(00000003)
    depth=0 C = GB, ST = London, L = London, O = blackhole.io, OU = blackhole.io, CN = blackhole.io, emailAddress = kura@blackhole.io
    ... snip ...
    ---
    220 blackhole.io [blackhole 1.7.0 (Stable)]
    HELO fake.mail.server
    250 OK
    MAIL FROM:<user@address.tld>
    250 OK
    RCPT TO:<someone@another.tld>
    250 OK
    DATA
    354 Start mail input; end with <CRLF>.<CRLF>
    To: Someone <someone@another.tld>
    From: User <user@address.tld>
    Subject: Bye

    Bye bye email
    .
    250 OK
    QUIT
    221 Thank you for speaking to me
    DONE

Testing STARTTLS
----------------

::

    $ openssl s_client -starttls smtp -connect blackhole.io:465
    CONNECTED(00000003)
    depth=0 C = GB, ST = London, L = London, O = blackhole.io, OU = blackhole.io, CN = blackhole.io, emailAddress = kura@blackhole.io
    ... snip ...
    ---
    250 DSN
    HELO fake.mail.server
    250 OK
    MAIL FROM:<user@address.tld>
    250 OK
    RCPT TO:<someone@another.tld>
    250 OK
    DATA
    354 Start mail input; end with <CRLF>.<CRLF>
    To: Someone <someone@another.tld>
    From: User <user@address.tld>
    Subject: Bye

    Bye bye email
    .
    250 OK
    QUIT
    221 Thank you for speaking to me
    DONE

Testing with Python
-------------------

.. code-block:: python
   :linenos:

    import smtplib

    msg = """From: <kura@kura.io>
    To: <kura@kura.io>
    Subject: Test

    gwergerg
    """

    server = smtplib.SMTP('blackhole.io', 25)
    server.sendmail("user@address.tld", "someone@another.tld", 
                msg)
    server.quit()

Getting the source code
=======================

The source code is available under the `MIT license`_ from `GitHub`_.

.. _MIT License: https://github.com/kura/blackhole/blob/master/LICENSE
.. _GitHub: https://github.com/kura/blackhole/

Running your own server
=======================

Python versions
---------------

::

    Python 2.6
    Python 2.7
    Python 3.2
    Python 3.3
    PyPy 1.9      # see notes below
    PyPy 2.0      # see notes below

Blackhole works on Python 2.6 and 2.7, it also works with PyPy (see :ref:`blackhole-pypy` section below).

Third party libraries
---------------------

::

    tornado>=2.2.1,<=3.1
    setproctitle>=1.1.6   # setproctitle 1.1.7 and above are required for all PyPy versions
    deiman>=0.1.5         # older version of Deiman will not work because of API changes

Getting started
---------------

.. toctree::
    :maxdepth: 2

    installation
    configuration-options
    configuration-file-example
    debug-flag
    delay-flag
    controlling-the-server
    controlling-the-server-init-d
    modes
    response-codes

FQDN
----

The FQDN that Blackhole will print on a new connection is automatically generated.

It will use the contents of `/etc/mailname`, if that file does not exist it will
use a name returned by `socket.getfqdn()`.

Tests & Coverage
================

Running tests manually
----------------------

Running tests manually is pretty simple, there is a Make target dedicated to it.

The test suite relies on `unittest2` and `nose`, both if which get installed by the Make target during test running.

::

    make tests

There is also a Make target for generating coverage::

    make coverage

Third party CI/Coverage
-----------------------

.. image:: https://api.travis-ci.org/kura/blackhole.png?branch=master
        :target: https://travis-ci.org/kura/blackhole

.. image:: https://coveralls.io/repos/kura/blackhole/badge.png?branch=master
        :target: https://coveralls.io/r/kura/blackhole

You can find the latest build status on `travis`_.

.. _travis: https://travis-ci.org/kura/blackhole

And the test coverage report on `coveralls`_.

.. _coveralls: https://coveralls.io/r/kura/blackhole

.. _blackhole-pypy:

Blackhole + PyPy
================

`PyPy`_ is a Python interpreter and just-in-time compiler. PyPy focuses on speed, efficiency and compatibility with the original CPython interpreter.

.. _PyPy: http://pypy.org/

Blackhole works well under PyPy 1.9, 2.0 beta1 and 2.0 beta2, you can see performance improvements
of up to 30% in certain situations.

However, blackhole does have issues with both PyPy 1.9 and 2.0 beta1 and 2.0 beta2 when using the pre-compiled binaries, this is due to a conflict in the version of OpenSSL compiled in to PyPy and the version compiled in to your CPython installation.
If you wish to use blackhole with SSL support on PyPy I suggest you either compile PyPy yourself or try to make sure your PyPy and CPython have the same versions.

FAQ
===

A few people have emailed me questions about why blackhole exists, how I use it, why Tornado and things like that
so I have outlined some questions and responses in an :ref:`faq`.

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
