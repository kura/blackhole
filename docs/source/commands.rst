.. _commands:

=====================================
Supported commands/verbs & parameters
=====================================

The following commands and parameters are supported by Blackhole.

- :ref:`helo`
- :ref:`ehlo`
- :ref:`help`
- :ref:`auth`
- :ref:`mail`
- :ref:`rcpt`
- :ref:`data`
- :ref:`quit`
- :ref:`rset`
- :ref:`vrfy`
- :ref:`noop`
- :ref:`etrn`
- :ref:`expn`

.. _helo:

HELO
====

.. code-block:: none

    >>> HELO domain.tld
    250 OK

.. _ehlo:

EHLO
====

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

.. _help:

HELP
====

.. code-block:: none

    >>> HELP
    250 Supported commands: AUTH DATA EHLO ETRN HELO MAIL NOOP QUIT RCPT RSET VRFY

.. _auth:

AUTH
====

Three authentication mechanisms are supported by Blackhole -- ``LOGIN``,
``PLAIN`` and ``CRAM-MD5``. More information on these mechanisms is available
in the `auth <command-auth.html>`_ section.

.. code-block:: none

    >>> AUTH PLAIN
    ...
    >>> AUTH LOGIN
    ...
    >>> AUTH CRAM-MD5
    ...

.. _mail:

MAIL
====

.. code-block:: none

    >>> MAIL FROM: <test@domain.tld>
    250 2.1.0 OK

You can specify the mime type using the ``BODY=`` parameter.

``7BIT``

.. code-block:: none

    >>> MAIL FROM: <test@domain.tld> BODY=7BIT
    250 2.1.0 OK

``8BITMIME``

.. code-block:: none

    >>> MAIL FROM: <test@domain.tld> BODY=8BITMIME
    250 2.1.0 OK

``SMTPUTF8``

.. code-block:: none

    >>> MAIL FROM: <test@domain.tld> SMTPUTF8
    250 2.1.0 OK

You can also specify the size using the ``SIZE=`` parameter.

.. code-block:: none

    >>> MAIL FROM: <test@domain.tld> SIZE=82000
    250 2.1.0 OK

.. _rcpt:

RCPT
====

.. code-block:: none

    >>> RCPT TO: <test@domain.tld>
    250 2.1.0 OK

.. _data:

DATA
====

.. code-block:: none

    >>> DATA
    354 End data with <CR><LF>.<CR><LF>
    >>> some email content
    >>> .

.. _quit:

QUIT
====

.. code-block:: none

    >>> QUIT
    221 2.0.0 Goodbye

.. _rset:

RSET
====

.. code-block:: none

    >>> RSET
    250 2.0.0 OK

.. _vrfy:

VRFY
====

Please see the `VRFY <command-vrfy.html>`_ section for information on the
``VRFY`` command, it's arguments and parameters and dynamically modifying it's
responses.

.. code-block:: none

    >>> VRFY test@domain.tld
    252 2.0.0 OK

.. _noop:

NOOP
====

.. code-block:: none

    >>> NOOP
    250 2.0.0 OK

.. _etrn:

ETRN
====

.. code-block:: none

    >>> ETRN
    250 Queueing started

.. _expn:

EXPN
====

Please see the `EXPN <command-expn.html>`_ section for information on the
``EXPN`` command, it's arguments and parameters and dynamically modifying it's
responses.

.. code-block:: none

    >>> EXPN list1
    250-Shadow <shadow@blackhole.io>
    250-Wednesday <wednesday@blackhole.io>
    250 Low-key Liesmith <low-key.liesmith@blackhole.io>
