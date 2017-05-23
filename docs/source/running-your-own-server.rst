.. _running-your-own-server:

=======================
Running your own server
=======================

Blackhole is built on top of `asyncio <https://docs.python.org/3/library/asyncio.html>`_
and utilises `async def <https://docs.python.org/3/reference/compound_stmts.html#async-def>`_
and `await <https://docs.python.org/3/reference/expressions.html#await>`_
statements available in Python 3.5 and above.

There are plenty of reasons for running your own server and it's very simple to
do. The base installation is a single line in length and the server will run
out-of-the-box.

Python < 3.5
------------

The original incarnation of Blackhole -- built on top of Tornado -- is still
available for use on Python versions lower than 3.5, including PyPy.

It is no longer maintained however, but is available for posterity's sake on
`GitHub <https://github.com/kura/blackhole/releases/tag/1.8.1>`_ for those
people unable to use Python 3.5.

Getting started
===============

.. toctree::
    :maxdepth: 2

    command-line-options
    configuration-options
    configuration-file-example
    delay-flag
    controlling-the-server-with-init-d
    modes
    response-codes

Installation
============

Packaged
--------

From `PyPI <https://pypi.python.org/pypi/blackhole>`_

.. code-block:: bash

  pip install blackhole

From GitHub
-----------

.. code-block:: bash

  pip install -e git+git://github.com/kura/blackhole.git#egg=blackhole

From source
-----------

Download the latest tarball from `PyPI <https://pypi.python.org/pypi/blackhole>`_
or `GitHub <https://github.com/kura/blackhole/tags>`_. Unpack and run:

.. code-block:: bash

  python setup.py install

Configuration
=============

For more information on the command line arguments see the
:ref:`command-line-options` document. For information on the configuration
options, their default values and what each option does, please see the
:ref:`configuration-options` document and, for an example
configuration file see :ref:`configuration-file-example`.
