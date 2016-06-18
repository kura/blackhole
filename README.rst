=========
Blackhole
=========

.. image:: https://img.shields.io/pypi/v/blackhole.svg?style=flat-square&label=version
    :target: https://pypi.python.org/pypi/blackhole
    :alt: Latest version released on PyPi

.. image:: https://img.shields.io/travis/kura/blackhole/master.svg?style=flat-square&label=build
    :target: http://travis-ci.org/kura/blackhole
    :alt: Build status of the master branch

.. image:: https://requires.io/github/kura/blackhole/requirements.svg?branch=master
     :target: https://requires.io/github/kura/blackhole/requirements/?branch=master
     :alt: Requirements Status

.. image:: https://img.shields.io/codecov/c/github/kura/blackhole/master.svg?style=flat-square&label=coverage
     :target: https://codecov.io/github/kura/blackhole/
     :alt: Test coverage

.. image:: https://img.shields.io/gitter/room/kura/blackhole.svg?style=flat-square
    :target: https://gitter.im/kura/blackhole
    :alt: Chat on Gitter

Blackhole is an `MTA (message transfer agent)
<https://en.wikipedia.org/wiki/Message_transfer_agent>`_ that (figuratively)
pipes all mail to /dev/null.

Blackhole is built on top of `asyncio
<https://docs.python.org/3/library/asyncio.html>`_ and utilises `async def <https://docs.python.org/3/reference/compound_stmts.html#async-def>`_
and `await <https://docs.python.org/3/reference/expressions.html#await>`_
statements available in `Python 3.5
<https://docs.python.org/3/whatsnew/3.5.html>`_ and above.

While blackhole is an MTA (mail transport agent), none of the actions
performed via SMTP or SMTPS are actually processed and no email or sent or
delivered.

You can tell blackhole how to handle mail that it receives. It can accept all
of it, bounce it all or randomly do either of those two actions. No matter how
you choose to configure it, the email is never actually delivered, it just
appears to have been delivered or bounced.

Think of blackhole sort of like a honeypot in terms of how it handles mail,
but it's specifically designed with testing in mind.

Service status
==============

You can find the current service status on `status.blackhole.io
<http://status.blackhole.io/>`_.

Donations
=========

Blackhole costs a bit of money to run, it receives millions of emails on a
daily basis, sometimes millions every 5 minutes depending on the load of the
platform.

To keep Blackhole running, please think about donating even just a little to
the project `via Gratipay <https://gratipay.com/blackhole.io/>`_.

Why?
====

Blackhole was first built when I was working on a project that required me to
be able to send/receive millions of emails per minute. As the sender was being
prototyped, I quickly realised that any mail server I pointed it at would fall
over due to the stess -- thus blackhole was born.

Documentation
=============

You can find the latest documentation `here <https://blackhole.io/>`_.

If you would like to contribute, please read the `contributors guide
<https://blackhole.io/contributing.html>`_.

The latest build status on `travis <https://travis-ci.org/kura/blackhole/>`_.

And the test coverage report on `codecov
<https://codecov.io/github/kura/blackhole/>`_.

Changelog
=========

You can find a list of changes `on the
blackhole website <https://blackhole.io/changelog.html>`_.
