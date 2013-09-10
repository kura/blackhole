.. _contributing:

============
Contributing
============

If you're thinking about contributing, it's really quite simple. There is no
need to feel daunted. You can contribute in a variety of ways:

- `Report bugs <https://github.com/kura/blackhole/issues>`_
- Submit pull requests for bug fixes or new behaviour
- Improve the documentation
- Write tests
- Improve performance
- Add additional support i.e. new versions of Python or PyPy
- Write additional engines, i.e. using Twisted instead of Tornado

Getting started
===============

Getting started is very similar to installation blackhole yourself. You should
familarise yourself with the documentation and
`PEP8 <http://www.python.org/dev/peps/pep-0008/>`_ Python style guide.

Writing some code
-----------------

You'll need to fork the blackhole repository and checkout the source to your
machine, much like any other project.

Once this is done, you need to run setup.py with the `develop` argument instead
of `install`.

.. code-block:: bash

    python setup.py develop

This will install all of blackhole's requirements for running the server.

You can do then simply branch and work away.

Things to do before submitting a pull request
---------------------------------------------

- Make sure that you written tests for what you have changed, or at least try
  to.
- Add your name to the CONTRIBUTORS list, feel free to add a comment about what
  you did i.e. `Kura added Twisted support`.
- Submit your pull request.

Running tests
=============

The Makefile supplied has a target for installing and running the test rig
against all currently supported versions of Python and PyPy, including a
documentation build test.

.. code-block:: bash

    make tox

If you'd only like to test against a single version of Python or PyPy you can
use the singular make target.

    make test

Lint and style guide tests
==========================

The Makefile contains a target for testing against PyFlakes and PEP8 using
flake8.

.. code-block:: bash

    make flake8

Building the documentation
==========================

The Makefile suppied also has a target for building the documentation.

.. code-block:: bash

    make docs
