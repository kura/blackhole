.. _contributing:

============
Contributing
============

If you're thinking about contributing, it's really quite simple. There is no
need to feel daunted. You can contribute in a variety of ways:

- `Report bugs <https://github.com/kura/blackhole/issues>`_
- Bug fixes
- New behaviour
- Improve the documentation
- Write tests
- Improve performance
- Add additional support i.e. new versions of Python or PyPy

Getting started
===============

Getting started is very similar to installing blackhole yourself. You should
familarise yourself with the documentation,
`PEP8 <http://www.python.org/dev/peps/pep-0008/>`_ Python style guide and
`PEP257 <https://www.python.org/dev/peps/pep-0257/>`_ docstring conventions.

Writing some code
-----------------

You'll need to fork the blackhole repository and checkout the source to your
machine, much like any other project.

You'll need to create a new branch for each piece of work you wish to do.

.. code-block:: bash

    git checkout -b branch_name

Once this is done, you need to run setup.py with the `develop` argument instead
of `install`.

.. code-block:: bash

    python setup.py develop

Now you can hackaway.

Things to do before submitting a pull request
---------------------------------------------

- Make sure that you've written tests for what you have changed, or at least
  try to.
- Add your name to the CONTRIBUTORS list, feel free to add a comment about what
  you did i.e. `Kura added STARTTLS support`.
- Submit your pull request.

.. _testing:

Running tests
=============

You can find the latest tests against the source code on `travis
<https://travis-ci.org/kura/blackhole/>`_.

Running tests manually is pretty simple, there is a `Makefile` target dedicated
to it.

The test suite relies on `py.test <http://pytest.org/latest/>`_ and is install
via the `Makefile` target and the `setup.py test` target.

.. code-block:: bash

    make test

To use the `setup.py test` target.

.. code-block:: bash

    python setup.py test

You can also test using `tox <https://tox.readthedocs.org/en/latest/>`_, this
will use the `detox <https://pypi.python.org/pypi/detox/>`_ library for
parallelising the tests. The `Makefile` target will install `py.test`, `tox`
and `detox` automatically.

.. code-block:: bash

    make tox

Lint and style guide tests
==========================

The Makefile contains a target for testing PEP8 and PEP257

.. code-block:: bash

    make lint

Building the documentation
==========================

The Makefile suppied also has a target for building the documentation.

.. code-block:: bash

    make docs
