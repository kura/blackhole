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
