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
    **EXPN** *[mailing-list]*

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
    **EXPN** *[all]*

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
