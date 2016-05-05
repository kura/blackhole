.. _vrfy:

====
VRFY
====

:Syntax:
    **VRFY** *user@domain.tld*

By default, VRFY will respond with a ``252`` response.

.. code-block:: none

    >>> VRFY user@domain.tld
    252 2.0.0 Will attempt delivery

You can explicitly tell it to return a ``250`` response.

.. code-block:: none

    >>> VRFY pass=user@domain.tld
    250 2.0.0 <pass=user@domain.tld> OK

Or explicitly tell it to fail.

.. code-block:: none

    >>> VRFY fail=user@domain.tld
    550 5.7.1 <fail=user@domain.tld> unknown
