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

.. _dynamic-switches:

================
Dynamic Switches
================

Dynamic switches allow you to tell blackhole how to respond to any given email.

For example, with default configuration blackhole will not delay while
responding to clients and will blindly accept all email. Using dynamic
switches, you can tell blackhole to bounce an email instead of accepting it or
delay for 10 seconds before processing the email -- without affecting any
other emails you are sending to the service.

Dynamic mode switches
=====================

Blackhole has three response modes, you can find out more about what the modes
are and the responses they send in the :ref:`mode` section.

Adding a dynamic mode switch header to an email message will make the blackhole
service respond to the email using that response mode.

The ``X-Blackhole-Mode`` header is responsible for dynamic mode switching.

.. code-block:: none

    From: Test <test@test.com>
    To: Test <test@test.com>
    Subject: A test
    X-Blackhole-Mode: bounce

    This email will be bounced because of the X-Blackhole-Mode header.

.. code-block:: none

    From: Another Test <a.test@test.com>
    To: Another Test <a.test@test.com>
    Subject: A second test
    X-Blackhole-Mode: accept

    This email will be accepted because of the X-Blackhole-Mode header.

Dynamic delay switches
======================

The ``X-Blackhole-Delay`` header is responsible for dynamic delay switching.

Delay for a set amount of time
------------------------------

.. code-block:: none

    From: Test <test@test.com>
    To: Test <test@test.com>
    Subject: A test
    X-Blackhole-Delay: 10

    Blackhole will delay for 10 seconds before responding.

Delay using a range
-------------------

.. code-block:: none

    From: Test <test@test.com>
    To: Test <test@test.com>
    Subject: A test
    X-Blackhole-Delay: 10, 60

    Blackhole will delay for between 10 and 60 seconds before responding to
    this email.

Combining dynamic switches
==========================

Because dynamic switches are just email headers, they can be combined.

.. code-block:: none

    From: Test <test@test.com>
    To: Test <test@test.com>
    Subject: A test
    X-Blackhole-Mode: bounce
    X-Blackhole-Delay: 10

    Blackhole will delay for 10 seconds before bouncing this email.

.. code-block:: none

    From: Test <test@test.com>
    To: Test <test@test.com>
    Subject: A test
    X-Blackhole-Mode: accept
    X-Blackhole-Delay: 10, 30

    Blackhole will delay for between 10 and 30 seconds before accepting
    this email.
