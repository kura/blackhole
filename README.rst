=========
Blackhole
=========

.. image:: https://api.travis-ci.org/kura/blackhole.png?branch=master
        :target: https://travis-ci.org/kura/blackhole

Tornado powered MTA for accepting all incoming emails 
without any disk I/O, although no messages actually ever 
get delivered. 
Mainly for testing huge send rates, for making sure developers
don't accidentally send emails to real users, email
integration testing and things like that.

Documentation
=============

You can find the latest documentation `here`_.

.. _here: http://blackhole.io

The latest build status on `travis`_.

.. _travis: https://travis-ci.org/kura/blackhole

And the test coverage report on `coveralls`_.

.. _coveralls: https://coveralls.io/r/kura/blackhole