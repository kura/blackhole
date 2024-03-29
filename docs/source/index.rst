..
    # (The MIT License)
    #
    # Copyright (c) 2013-2021 Kura
    #
    # Permission is hereby granted, free of charge, to any person obtaining a
    # copy of this software and associated documentation files (the
    # 'Software'), to deal in the Software without restriction, including
    # without limitation the rights to use, copy, modify, merge, publish,
    # distribute, sublicense, and/or sell copies of the Software, and to permit
    # persons to whom the Software is furnished to do so, subject to the
    # following conditions:
    #
    # The above copyright notice and this permission notice shall be included
    # in all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS
    # OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    # MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
    # NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
    # DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
    # OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
    # USE OR OTHER DEALINGS IN THE SOFTWARE.

====================================
Blackhole |githubactions| |coverage|
====================================

Blackhole is an `MTA (message transfer agent)
<https://en.wikipedia.org/wiki/Message_transfer_agent>`_ that (figuratively)
pipes all mail to /dev/null, built on top of `asyncio
<https://docs.python.org/3/library/asyncio.html>`_ and utilises `async def <https://docs.python.org/3/reference/compound_stmts.html#async-def>`_ and `await
<https://docs.python.org/3/reference/expressions.html#await>`_ statements
available in `Python 3.5 <https://docs.python.org/3/whatsnew/3.5.html>`_.

While Blackhole is an MTA, none of the actions performed via SMTP or SMTPS are
actually processed, and no email is delivered. You can tell Blackhole how to
handle mail that it receives. It can accept all of it, bounce it all, or
randomly do either of those two actions.

Think of Blackhole sort of like a honeypot in terms of how it handles mail, but
it's specifically designed with testing in mind.


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


.. |githubactions| image:: https://img.shields.io/github/workflow/status/kura/blackhole/CI?style=for-the-badge&label=tests&logo=githubactions
    :target: https://github.com/kura/blackhole/actions/workflows/ci.yml
    :alt: Build status of the master branch

.. |coverage| image:: https://img.shields.io/codecov/c/github/kura/blackhole/master.svg?style=for-the-badge&label=coverage&logo=codecov
    :target: https://codecov.io/github/kura/blackhole/
    :alt: Test coverage
