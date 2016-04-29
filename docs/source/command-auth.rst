.. _auth:

====
AUTH
====

AUTH PLAIN
==========

:Syntax:
    **AUTH PLAIN** *[additional]*

By default, ``AUTH PLAIN`` will succeed unless you ask it not to.

Succeed
-------

.. code-block:: none

    >>> AUTH PLAIN
    334
    >>> fail=letmein
    535 5.7.8 Authentication failed

.. code-block:: none

    >>> AUTH PLAIN pass=letmein
    235 2.7.0 Authentication successful

Fail
----

.. code-block:: none

    >>> AUTH PLAIN
    334
    >>> pass=letmein
    235 2.7.0 Authentication successful

.. code-block:: none

    >>> AUTH PLAIN fail=letmein
    535 5.7.8 Authentication failed


AUTH LOGIN
==========

:Syntax:
    **AUTH LOGIN**

By default, ``AUTH PLAIN`` will succeed unless you ask it not to.

Succeed
-------

.. code-block:: none

    >>> AUTH LOGIN:
    334 VXNlcm5hbWU6
    >>> pass=letmein
    235 2.7.0 Authentication successful

Fail
----

.. code-block:: none

    >>> AUTH LOGIN:
    334 VXNlcm5hbWU6
    >>> fail=letmein
    535 5.7.8 Authentication failed

AUTH CRAM-MD5
=============

:Syntax:
    **AUTH CRAM-MD5**

By default, ``AUTH PLAIN`` will succeed unless you ask it not to.

Succeed
-------

.. code-block:: none

    >>> AUTH CRAM-MD5
    334 PDE0NjE5MzA1OTYwMS4yMDQ5LjEyMz...
    >>> pass=letmein
    235 2.7.0 Authentication successful

Fail
----

.. code-block:: none

    >>> AUTH CRAM-MD5
    334 PDE0NjE5MzA1OTYwMS4yMDQ5LjEyMz...
    >>> fail=letmein
    535 5.7.8 Authentication failed
