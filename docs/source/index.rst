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
    220 2.2.0 OK, ready
    HELO fake.mail.server
    250 2.5.0 OK, done
    MAIL FROM:<user@address.tld>
    250 2.5.0 OK, done
    RCPT TO:<someone@another.tld>
    250 2.5.0 OK, done
    DATA
    354 3.5.4 Start mail input; end with <CRLF>.<CRLF>
    To: Someone <someone@another.tld>             
    From: User <user@address.tld>
    Subject: Bye
    
    Bye bye email
    .
    251 2.5.1 OK, user not local, will forward
    QUIT
    221 2.2.1 Thank you for speaking to me
    Connection closed by foreign host.

Testing SSL
-----------

::

    $ openssl s_client -connect blackhole.io:465
    CONNECTED(00000003)
    depth=0 C = GB, ST = London, L = London, O = blackhole.io, OU = blackhole.io, CN = blackhole.io, emailAddress = kura@blackhole.io
    ... snip ...
    ---
    220 2.2.0 OK, ready
    HELO fake.mail.server
    250 2.5.0 OK, done
    MAIL FROM:<user@address.tld>
    250 2.5.0 OK, done
    RCPT TO:<someone@another.tld>
    250 2.5.0 OK, done
    DATA
    354 3.5.4 Start mail input; end with <CRLF>.<CRLF>
    To: Someone <someone@another.tld>             
    From: User <user@address.tld>
    Subject: Bye
    
    Bye bye email
    .
    251 2.5.1 OK, user not local, will forward
    QUIT
    221 2.2.1 Thank you for speaking to me
    DONE

Getting the source code
=======================

The source code is available under the `MIT license`_ from `GitHub`_.

.. _MIT License: https://github.com/kura/blackhole/blob/master/LICENSE
.. _GitHub: https://github.com/kura/blackhole/

Running your own server
=======================

.. toctree::
    :maxdepth: 2

    installation
    configuration-options
    configuration-file-example
    controlling-the-server
    controlling-the-server-init-d
    modes
    response-codes

Tests & Coverage
================

.. image:: https://api.travis-ci.org/kura/blackhole.png?branch=master
        :target: https://travis-ci.org/kura/blackhole

You can find the latest build status on `travis`_.

.. _travis: https://travis-ci.org/kura/blackhole

And the test coverage report on `coveralls`_.

.. _coveralls: https://coveralls.io/r/kura/blackhole

Blackhole + PyPy
================

`PyPy`_ is a Python interpreter and just-in-time compiler. PyPy focuses on speed, efficiency and compatibility with the original CPython interpreter.

.. _PyPy: http://pypy.org/

Blackhole works well under PyPy 1.9, 2.0 beta1 and 2.0 beta2, you can see performance improvements
of up to 30% in certain situations. 

However, blackhole does have issues with both PyPy 1.9 and 2.0 beta1 and 2.0 beta2 when using the pre-compiled binaries, this is due to a conflict in the version of OpenSSL compiled in to PyPy and the version compiled in to your CPython installation.
If you wish to use blackhole with SSL support on PyPy I suggest you either compile PyPy yourself or try to make sure your PyPy and CPython have the same versions.

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
