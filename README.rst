=========
Blackhole
=========

.. image:: https://api.travis-ci.org/kura/blackhole.png?branch=master
        :target: https://travis-ci.org/kura/blackhole

.. image:: https://codecov.io/github/kura/blackhole2/coverage.svg?branch=master
        :target: https://codecov.io/github/kura/blackhole2?branch=master

Blackhole is an email MTA that pipes all mail to /dev/null.

Blackhole is built on top of asyncio and utilises `async` and `await`
statements on available in Python 3.5 and above.

While Blackhole is an MTA (mail transport agent), none of the actions
performed of SMTP or SMTPS are actually processed and no email or sent or
delivered.

Documentation
=============

You can find the latest documentation `here <http://blackhole.io>`_.

If you would like to contribute, please read the `contributors guide
<https://blackhole.io/contributing.html>`_.

The latest build status on `travis <https://travis-ci.org/kura/blackhole2/>`_.

And the test coverage report on `codecov
<https://codecov.io/github/kura/blackhole2?branch=master>`_.
