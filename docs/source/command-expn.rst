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

.. _expn:

====
EXPN
====

The EXPN command/verb can be asked to respond in several ways.

EXPN without an argument
========================

:Syntax:
    **EXPN**

Calling the ``EXPN`` command with no arguments or an invalid mailing list name
will cause it to return an error.

.. code-block:: none

    >>> EXPN
    550 Not authorised

.. code-block:: none

    >>> EXPN some-list
    550 Not authorised

You can also explicitly tell ``EXPN`` to fail by passing ``fail=`` as part of
the mailing list name.

.. code-block:: none

    >>> EXPN fail=test-list
    550 Not authorised

EXPN <list>
===========

:Syntax:
    **EXPN** *mailing-list*

Three lists are built-in to Blackhole for use.

``list1``, ``list2`` and ``list3`` and can be used as follows.

list1
-----

.. code-block:: none

    >>> EXPN list1
    250-Shadow <shadow@blackhole.io>
    250-Wednesday <wednesday@blackhole.io>
    250 Low-key Liesmith <low-key.liesmith@blackhole.io>

list2
-----

.. code-block:: none

    >>> EXPN list2
    250-Jim Holden <jim.holden@blackhole.io>
    250-Naomi Nagata <naomi.nagata@blackhole.io>
    250-Alex Kamal <alex.kamal@blackhole.io>
    250 Amos Burton <amos.burton@blackhole.io>

list3
-----

.. code-block:: none

    >>> EXPN list3
    250-Takeshi Kovacs <takeshi.kovacs@blackhole.io>
    250-Laurens Bancroft <laurens.bancroft@blackhole.io>
    250-Kristin Ortega <kristin.ortega@blackhole.io>
    250-Quellcrist Falconer <quellcrist.falconer@blackhole.io>
    250-Virginia Vidaura <virginia.vidaura@blackhole.io>
    250 Reileen Kawahara <reileen.kawahara@blackhole.io>

EXPN all
========

:Syntax:
    **EXPN** *all*

The ``all`` argument combines all three lists and returns them.

.. code-block:: none

    >>> EXPN all
    250-Jim Holden <jim.holden@blackhole.io>
    250-Naomi Nagata <naomi.nagata@blackhole.io>
    250-Alex Kamal <alex.kamal@blackhole.io>
    250-Amos Burton <amos.burton@blackhole.io>
    250-Shadow <shadow@blackhole.io>
    250-Wednesday <wednesday@blackhole.io>
    250-Low-key Liesmith <low-key.liesmith@blackhole.io>
    250-Takeshi Kovacs <takeshi.kovacs@blackhole.io>
    250-Laurens Bancroft <laurens.bancroft@blackhole.io>
    250-Kristin Ortega <kristin.ortega@blackhole.io>
    250-Quellcrist Falconer <quellcrist.falconer@blackhole.io>
    250-Virginia Vidaura <virginia.vidaura@blackhole.io>
    250 Reileen Kawahara <reileen.kawahara@blackhole.io>
