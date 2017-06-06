============================
Communicating with Blackhole
============================

With Python
===========

.. code-block:: python

    # from smtplib import SMTP             # For sending without SSL/TLS.
    from smtplib import SMTP_SSL

    server = 'blackhole.io'  # Change this to your server address.
    msg = '''From: <test@blackhole.io>
    To: <test@blackhole.io>
    Subject: Test email

    Random test email. Some UTF-8 characters: ßæøþ'''

    # smtp = SMTP(server, 25)      # For sending without SSL/TLS.
    smtp = SMTP_SSL(server, 465)
    smtp.sendmail('test@blackhole.io', 'test@blackhole.io',
                  msg.encode('utf-8'))

    # We can send multiple messages using the same connection.
    smtp.sendmail(server, 'tset@blackhole.io',
                  msg.encode('utf-8'))

    # Quit after we're done
    smtp.quit()


.. _commands:

Supported commands/verbs & parameters
=====================================

- :ref:`auth`
- `DATA`_
- `EHLO`_
- `ETRN`_
- :ref:`expn`
- `HELO`_
- `HELP`_
- `MAIL`_ **BODY=** `7BIT`_, `8BITMIME`_, `SMTPUTF8`_ **SIZE=** `SIZE`_
- `NOOP`_
- `QUIT`_
- `RCPT`_
- `RSET`_
- :ref:`vrfy`

-----

.. _DATA:

DATA
----

:Syntax:
    **DATA**

.. code-block:: none

    >>> DATA
    354 End data with <CR><LF>.<CR><LF>
    >>> some email content
    >>> .

-----

.. _EHLO:

EHLO
----

:Syntax:
    **EHLO** *domain.tld*

.. code-block:: none

    >>> EHLO domain.tld
    250-blackhole.io
    250-HELP
    250-PIPELINING
    250-AUTH CRAM-MD5 LOGIN PLAIN
    250-SIZE
    250-VRFY
    250-ETRN
    250-ENHANCEDSTATUSCODES
    250-8BITMIME
    250-SMTPUTF8
    250 DSN

-----

.. _ETRN:

ETRN
----

:Syntax:
    **ETRN**

.. code-block:: none

    >>> ETRN
    250 Queueing started

-----

.. _HELO:

HELO
----

:Syntax:
    **HELO** *domain.tld*

.. code-block:: none

    >>> HELO domain.tld
    250 OK

-----

.. _HELP:

HELP
----

:Syntax:
    **HELP**
:Optional:
    *COMMAND*

.. code-block:: none

    >>> HELP
    250 Supported commands: AUTH DATA EHLO ETRN HELO MAIL NOOP QUIT RCPT RSET
                            VRFY

-----

.. _MAIL:
.. _7BIT:
.. _8BITMIME:
.. _SMTPUTF8:

MAIL
----

:Syntax:
    **MAIL FROM:** *<user@domain.tld>*
:Optional:
    BODY= *7BIT, 8BITMIME*
:Optional:
    *SMTPUTF8*
:Optional:
    SIZE= *SIZE*

.. code-block:: none

    >>> MAIL FROM: <test@domain.tld>
    250 2.1.0 OK

BODY=
~~~~~

.. code-block:: none

    >>> MAIL FROM: <test@domain.tld> BODY=7BIT
    250 2.1.0 OK

.. code-block:: none

    >>> MAIL FROM: <test@domain.tld> BODY=8BITMIME
    250 2.1.0 OK

.. code-block:: none

    >>> MAIL FROM: <test@domain.tld> SMTPUTF8
    250 2.1.0 OK

.. _SIZE:

SIZE=
~~~~~

You can also specify the size using the ``SIZE=`` parameter.

.. code-block:: none

    >>> MAIL FROM: <test@domain.tld> SIZE=82000
    250 2.1.0 OK

-----

.. _NOOP:

NOOP
----

:Syntax:
    **NOOP**

.. code-block:: none

    >>> NOOP
    250 2.0.0 OK

-----

.. _QUIT:

QUIT
----

:Syntax:
    **QUIT**

.. code-block:: none

    >>> QUIT
    221 2.0.0 Goodbye

-----

.. _RCPT:

RCPT
----

:Syntax:
    **RCPT TO:** *<user@domain.tld>*

.. code-block:: none

    >>> RCPT TO: <test@domain.tld>
    250 2.1.0 OK

-----

.. _RSET:

RSET
----

:Syntax:
    **RSET**

.. code-block:: none

    >>> RSET
    250 2.0.0 OK


.. _response-codes:

Response codes
==============

Accept codes
------------

::

    250: 2.0.0 OK: queued as MESSAGE-ID

Bounce codes
------------

::

    450: Requested mail action not taken: mailbox unavailable
    451: Requested action aborted: local error in processing
    452: Requested action not taken: insufficient system storage
    458: Unable to queue message
    521: Machine does not accept mail
    550: Requested action not taken: mailbox unavailable
    551: User not local
    552: Requested mail action aborted: exceeded storage allocation
    553: Requested action not taken: mailbox name not allowed
    571: Blocked