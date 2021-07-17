=========
Blackhole
=========

.. image:: https://img.shields.io/github/workflow/status/kura/blackhole/CI?style=for-the-badge&label=tests&logo=githubactions
    :target: https://github.com/kura/blackhole/actions/workflows/ci.yml
    :alt: Build status of the master branch

.. image:: https://img.shields.io/codecov/c/github/kura/blackhole/master.svg?style=for-the-badge&label=coverage&logo=codecov
    :target: https://codecov.io/github/kura/blackhole/
    :alt: Test coverage

Blackhole is an `MTA (message transfer agent)
<https://en.wikipedia.org/wiki/Message_transfer_agent>`_ that (figuratively)
pipes all mail to /dev/null, built on top of `asyncio
<https://docs.python.org/3/library/asyncio.html>`_ and utilises `async def <https://docs.python.org/3/reference/compound_stmts.html#async-def>`_
and `await
<https://docs.python.org/3/reference/expressions.html#await>`_ statements
available in `Python 3.5 <https://docs.python.org/3/whatsnew/3.5.html>`_.

While Blackhole is an MTA, none of the actions performed via SMTP or SMTPS are
actually processed, and no email is delivered. You can tell Blackhole how to
handle mail that it receives. It can accept all of it, bounce it all, or
randomly do either of those two actions.

Think of Blackhole sort of like a honeypot in terms of how it handles mail, but
it's specifically designed with testing in mind.

Python support
==============

- Python 3.7+
- PyPy 3.7+
- Pyston 2.2+

Documentation
=============

You can find the latest documentation `here
<https://kura.gg/blackhole/>`_.

If you would like to contribute, please read the `contributors guide
<https://kura.gg/blackhole/overview.html#contributing>`_.

The latest build status on GitHub `<https://github.com/kura/blackhole/actions/workflows/ci.yml>`_.

And the test coverage report on `codecov
<https://codecov.io/github/kura/blackhole/>`_.

Changelog
=========

You can find a list of changes `on the
blackhole website <https://kura.gg/blackhole/changelog.html>`_.
