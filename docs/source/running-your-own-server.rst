.. _running-your-own-server:

=======================
Running your own server
=======================

Blackhole is built on top of `asyncio <https://docs.python.org/3/library/asyncio.html>`_
and utilises `async def <https://docs.python.org/3/reference/compound_stmts.html#async-def>`_
and `await <https://docs.python.org/3/reference/expressions.html#await>`_
statements available in Python 3.5 and above and the `pathlib
<https://docs.python.org/3/library/pathlib.html#module-pathlib>`_ module made
available by Python 3.6.

There are plenty of reasons for running your own server and it's very simple to
do. The base installation is a single line in length and the server will run
out-of-the-box.

Python < 3.6
------------

The original incarnation of Blackhole -- built on top of Tornado -- is still
available for use on Python versions lower than 3.6, including PyPy.

It is no longer maintained however, but is available for posterity's sake on
github_tag_ for those people unable to use Python 3.6.

.. _github_tag: https://github.com/kura/blackhole/releases/tag/1.8.1

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

From pypi_

.. code-block:: bash

  pip install blackhole

From GitHub
-----------

.. code-block:: bash

  pip install -e git+git://github.com/kura/blackhole.git#egg=blackhole

From source
-----------

Download the latest tarball from pypi_ or github_tags_. Unpack and run:

.. _github_tags: https://github.com/kura/blackhole/tags

.. code-block:: bash

  python setup.py install

.. _pypi: https://pypi.python.org/pypi/blackhole

Configuration
=============

For more information on the command line arguments see the
:ref:`command-line-options` document. For information on the configuration
options, their default values and what each option does, please see the
:ref:`configuration-options` document and, for an example
configuration file see :ref:`configuration-file-example`.
