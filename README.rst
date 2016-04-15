=========
Blackhole
=========

Blackhole is an email MTA that pipes all mail to /dev/null.

Blackhole is built on top of asyncio and utilises `async` and `await`
statements on available in Python 3.5 and above.

While Blackhole is an MTA (mail transport agent), none of the actions
performed of SMTP or SMTPS are actually processed and no email or sent or
delivered.

-----

|pypi| |travis| |coverage| |gitter|

-----

Documentation
=============

You can find the latest documentation `here <http://blackhole.io/2>`_.

If you would like to contribute, please read the `contributors guide
<https://blackhole.io/2/contributing.html>`_.

The latest build status on `travis <https://travis-ci.org/kura/blackhole2/>`_.

And the test coverage report on `coveralls
<https://coveralls.io/github/kura/blackhole2?branch=master>`_.

.. |pypi| image:: https://img.shields.io/pypi/v/blackhole2.svg?style=flat-square&label=latest%20stable%20version
    :target: https://pypi.python.org/pypi/blackhole2
    :alt: Latest version released on PyPi

.. |coverage| image:: https://img.shields.io/coveralls/kura/blackhole2/master.svg?style=flat-square&label=coverage
    :target: https://coveralls.io/r/kura/blackhole2?branch=master
    :alt: Test coverage

.. |travis| image:: https://img.shields.io/travis/kura/blackhole2/master.svg?style=flat-square&label=build
    :target: http://travis-ci.org/kura/blackhole2
    :alt: Build status of the master branch

.. |gitter| image:: https://badges.gitter.im/kura/blackhole2.svg
    :target: https://gitter.im/kura/blackhole2
    :alt: Chat on Gitter
