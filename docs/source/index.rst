=============================================
Blackhole |pypi| |travis| |coverage| |gitter|
=============================================

Blackhole is an `MTA (message transfer agent)
<https://en.wikipedia.org/wiki/Message_transfer_agent>`_ that (figuratively)
pipes all mail to /dev/null, built on top of `asyncio
<https://docs.python.org/3/library/asyncio.html>`_ and utilises `async def <https://docs.python.org/3/reference/compound_stmts.html#async-def>`_
and `await <https://docs.python.org/3/reference/expressions.html#await>`_
statements available in `Python 3.5
<https://docs.python.org/3/whatsnew/3.5.html>`_.

While Blackhole is an MTA, none of the actions performed via SMTP or SMTPS are
actually processed and no email is delivered.

You can tell Blackhole how to handle mail that it receives. It can accept all
of it, bounce it all or randomly do either of those two actions.

Think of Blackhole sort of like a honeypot in terms of how it handles mail,
but it's specifically designed with testing in mind.


User Guide
==========

.. toctree::
    :maxdepth: 3

    overview
    configuration
    communicating-with-blackhole
    dynamic-responses
    dynamic-switches
    api


.. |pypi| image:: https://img.shields.io/pypi/v/blackhole.svg?style=flat-square&label=version
    :target: https://pypi.python.org/pypi/blackhole
    :alt: Latest version released on PyPi

.. |travis| image:: https://img.shields.io/travis/kura/blackhole/master.svg?style=flat-square&label=build
    :target: http://travis-ci.org/kura/blackhole
    :alt: Build status of the master branch

.. |coverage| image:: https://img.shields.io/codecov/c/github/kura/blackhole/master.svg?style=flat-square&label=coverage
    :target: https://codecov.io/github/kura/blackhole/
    :alt: Test coverage

.. |gitter| image:: https://img.shields.io/gitter/room/kura/blackhole.svg?style=flat-square
    :target: https://gitter.im/kura/blackhole
    :alt: Chat on Gitter
