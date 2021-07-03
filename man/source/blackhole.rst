=========
Blackhole
=========

-------------------------------------------------------
An MTA that (figuratively) pipes all mail to /dev/null.
-------------------------------------------------------

:Manual section: 1

SYNOPSIS
========

blackhole [OPTIONS]

DESCRIPTION
===========

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

OPTIONS
=======

-h			show this help message and exit
-v			show program's version number and exit
-c FILE		override the default configuration options
-t			perform a configuration test and exit
-d			enable debugging mode
-b			run in the background
-ls			Disable `ssl.OP_SINGLE_DH_USE` and `ssl.OP_SINGLE_ECDH_USE`.
			Reduces CPU overhead at the expense of security. Don't use this
			option unless you really need to.
-q			Suppress warnings when using -ls/--less-secure, running as root or
			not using `tls_dhparams` option.

SEE ALSO
========

- **blackhole_config** (1)
- `<https://kura.gg/blackhole/configuration.html>`_

LICENSE
=======

The MIT license must be distributed with this software.

AUTHOR(S)
=========

Kura <kura@kura.gg>
