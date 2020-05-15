..
    # (The MIT License)
    #
    # Copyright (c) 2013-2020 Kura
    #
    # Permission is hereby granted, free of charge, to any person obtaining a copy
    # of this software and associated documentation files (the 'Software'), to deal
    # in the Software without restriction, including without limitation the rights
    # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    # copies of the Software, and to permit persons to whom the Software is
    # furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in
    # all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    # SOFTWARE.

.. _auth:

====
AUTH
====

AUTH PLAIN
==========

:Syntax:
    **AUTH PLAIN**
:Optional:
    *auth data*

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
