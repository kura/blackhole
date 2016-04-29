.. _dynamic-responses:

=================
Dynamic responses
=================

Some commands allow you to define how they respond. For instance, telling an
``AUTH`` command or ``VRFY`` command to fail.

You can specify ``pass=`` or ``fail=`` as part of a client request to trigger
it to succeed or fail, as you require.

Below is a list of commands/verbs that allow you to modify their behaviour
on-the-fly, including how they can be modified and what they return.

.. toctree::
   :maxdepth: 2

   command-auth
   command-vrfy
   command-expn
