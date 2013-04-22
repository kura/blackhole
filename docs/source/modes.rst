.. _modes:

Modes
=====

The server can run in several different modes, these are outlined below.

See the :ref:`response-codes` section for more information on responses
and which mode responds with which codes.

accept
======

Accept all email with code 250, 251, 252 or 253.

bounce
======

Bounce all email with a random code, excluding 250, 251, 252, 253.

random
======

Randomly accept or bounce all email with a random code.

unavailable
===========

Server always respondes with code 421 - service is unavailable.

offline
=======

Server always responds with code 521 - server does not accept mail.