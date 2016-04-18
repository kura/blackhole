.. _running-your-own-server:

=======================
Running your own server
=======================

Blackhole is built on top of `asyncio <https://docs.python.org/3/library/asyncio.html>`_
and utilises `async def <https://docs.python.org/3/reference/compound_stmts.html#async-def>`_
and `await <https://docs.python.org/3/reference/expressions.html#await>`_
statements available in Python 3.5 and above.

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

For more information on the command line arguments read :ref:`command-line-options`
configuration file format read :ref:`configuration-file-example`.
