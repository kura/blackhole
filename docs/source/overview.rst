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

========
Overview
========

.. _requirements:

Requirements
============

- Python 3.6

.. note::

    The original incarnation of Blackhole -- built on top of Tornado -- is still
    available for use on Python versions lower than 3.6, including PyPy.

    It is no longer maintained however, but is available for posterity's sake on
    `GitHub <https://github.com/kura/blackhole/tree/1.8.1>`__ for those people
    unable to use Python 3.6.


.. _installation:

Installation
============

PyPI
----

.. code-block:: bash

  pip install blackhole

Source
------

Download the latest tarball from `PyPI
<https://pypi.python.org/pypi/blackhole>`_ or `GitHub
<https://github.com/kura/blackhole/tags>`__. Unpack and run:

.. code-block:: bash

  python setup.py install


.. _license:

License
=======

Blackhole is licensed under the `MIT license
<https://github.com/kura/blackhole/blob/master/LICENSE>`_.

    (The MIT License)

    Copyright (c) 2013-2020 Kura

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the 'Software'), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.


.. _contributing:

Contributing
============

If you're thinking about contributing, it's really quite simple. There is no
need to feel daunted. You can contribute in a variety of ways:

- `Report bugs <https://github.com/kura/blackhole/issues>`_,
- `fix bugs <https://github.com/kura/blackhole/issues>`_,
- `add new behaviour <https://kura.github.io/blackhole/todo.html>`_,
- `improve the documentation
  <https://github.com/kura/blackhole/tree/master/docs/source>`_,
- `write tests <https://github.com/kura/blackhole/tree/master/tests>`_,
- improve performance, and
- add additional support i.e. new versions of Python or PyPy.

Please make sure that you read, understand and accept the `Code of Conduct
<https://github.com/kura/blackhole/blob/master/CODE_OF_CONDUCT.rst>`__.

You can view a list of tasks that need work on the :ref:`todo` page.

The :ref:`api` section also has a wealth of information on how the server works
and how you can modify it or use parts of it.

Getting started
---------------

Getting started is very similar to installing blackhole yourself. You should
familarise yourself with the documentation,
`PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ Python style guide and
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
-------------

You can find the latest tests against the source code on `travis
<https://travis-ci.org/kura/blackhole/>`_.

Running tests manually is pretty simple, there is a `Makefile` target dedicated
to it.

The test suite relies on `py.test <https://docs.pytest.org/en/latest/>`_ and is
installed via the `Makefile` target and the `setup.py test` target.

The test suite takes a while to run, there are a lot of parts that require
communication and also use calls :any:`asyncio.sleep`, which cause the test
suite to pause until the sleep is done.

.. code-block:: bash

    make test

To use the `setup.py test` target.

.. code-block:: bash

    python setup.py test

You can also test using `tox <https://tox.readthedocs.io/en/latest/>`_,
when run through the `Makefile` `tox` will be installed automatically and the
tests will be parallelised.

.. code-block:: bash

    make tox

Building the documentation
--------------------------

The Makefile suppied also has a target for building the documentation.

.. code-block:: bash

    make docs


Upcoming/planned features
=========================

.. toctree::
    :maxdepth: 3

    todo


Changelog
=========

.. toctree::
    :maxdepth: 3

    changelog
