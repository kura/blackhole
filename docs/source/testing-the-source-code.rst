.. _testing-the-source-code:

=======================
Testing the source code
=======================

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
