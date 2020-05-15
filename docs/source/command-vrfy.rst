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
