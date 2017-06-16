.. _changelog:

=========
Changelog
=========

-------------------------
Upcoming/planned features
-------------------------

There is a list of upcoming/planned features on the :ref:`todo` page.

Two of the biggest upcoming features will be
`POP3 <https://en.wikipedia.org/wiki/Post_Office_Protocol>`_ and
`IMAP4 <https://en.wikipedia.org/wiki/Internet_Message_Access_Protocol>`_
support, to help with email client development, tesing and whatever else you
want to use it for.

If you have a feature you need or would like, feel free to put an issue on the
`issue tracker <https://github.com/kura/blackhole/issues>`_ or take a look at
the :ref:`contributing` section for information on how you could implement
the functionality yourself.

---------------
Current release
---------------

2.1.8
=====

.. _2.1.8:

- Mostly a bugfix release.
- Added new command ``blackhole_config`` to display config options on command
  line.

-------------
Past releases
-------------

.. _2.1.7:
.. _2.1.6:

- Introduced the ability to use `uvloop
  <https://github.com/MagicStack/uvloop>`_ in place of the default
  :py:obj:`asyncio.event_loop`.

.. _2.1.4:
.. _2.1.5:

2.1.5
=====

The 2.1.5 release is actually a tiny bug fix release that I'm combining with
the large 2.1.4 release.

- Bugfix for :py:obj:`socket.SO_REUSEPORT`.
- Squashed bugs related to :py:func:`socket.socket` failing in child processes.
  These squashed bugs fix IPv6 which had a tendency of not working as expected.
- Added communication between supervisor and children, allow children to be
  restarted if they fail to communicate to the supervisor.
- Added ``mode=`` and ``delay=`` optionals to the :ref:`listen` and
  :ref:`tls_listen` directives. Allowing listeners to spawn on specific ports
  and act in different ways.

  When ``mode`` and ``delay`` are configured in a listener directive, that
  listener will ignore the global mode and delay options for that listener.
  Setting :ref:`mode` and :ref:`delay` on a listener will also disable
  :ref:`dynamic-switches` for that listener, automatically.
- Internal module loading changes
- Added test utilities to the test suite.
- The blackhole environment will be reset for each test.
- Added a lot of testing to supervisor, worker and child functionality.
- Added a ``--quiet`` mode to suppress warnings when using
  ``-ls/--less-secure``, running as the root user or not using the
  :ref:`tls_dhparams` option.
- Added a warning when running the server as the root user without specifing
  a reduced privilege :ref:`user` and :ref:`group`.
- Improved shutdown procedure, now does a much better job of disconnecting
  clients and closing everything before exiting.
- Added an internal counter of invalid SMTP commands. Mitigate DoS attacks,
  maximum failed commands per connection is 10. Clients that violate this rule
  get disconnected.

.. _2.1.3:

2.1.3
=====

- Squashed a bug that caused children to not properly apply their TLS context.

.. _2.1.2:

2.1.2
=====

- Squashed a bug that caused workers to be spawned with their old privileges
  when combined with the ``-d`` or ``--daemon`` flags and a reduced privilege
  user and group.
- Squashed a bug that caused the pid file to retain old privileges when given
  a reduced privilege user and group and the ``-d`` or ``--daemon`` flags.

.. _2.1.1:
.. _2.1.0:

2.1.1
=====

*(This is actually the planned 2.1.0 release, but PyPI refused to let me use
that version number)*

- Fix ``SIZE=`` being parsed in the ``MAIL`` verb.
- Huge overhaul of testing, finally almost all of :class:`blackhole.smtp.Smtp`
  is tested.
- Added worker processes.

.. _2.0.14:

2.0.14
======

- SMTP Submission (port 587) is automatically used as a listener alongside port
  25.
- Added ``SIZE=`` checks in ``MAIL FROM`` command, rather than waiting until
  ``DATA``.
- Added EXPN verb. -- :ref:`expn`
- Updated many verbs to allow on-the-fly modification of return codes. --
  :ref:`dynamic-responses`
- Added a list of :ref:`commands`

.. _2.0.13:

2.0.13
======

- Fixed a misspelled TLS cipher. ``CDHE-ECDSA-AES128-GCM-SHA256`` should have
  been written as ``ECDHE-ECDSA-AES128-GCM-SHA256``. This typo simply meant
  that cipher was unavailable for use, the other nine strong ciphers were/are
  still fully available.
- :ref:`configuration-options` document compiled.
- In-line comments in configuration files are now supported and the comment is
  ignored.

.. code-block:: ini

    listen = :25, :::25  # IPv4 and IPv6

Will be read as.

.. code-block:: ini

    listen = :25, :::25

- Large scale documentation updates. Pretty much everything should be fully
  documented now, including all :py:exc:`SystemExit` calls including their
  return codes.
- Added an option to disable :py:obj:`ssl.OP_SINGLE_DH_USE` and
  :py:obj:`ssl.OP_SINGLE_ECDH_USE`. Reduces CPU overhead at the expense
  of security. Disabled by default, warns if used. Slightly better for high
  load environments. -- :ref:`command-line-options`

.. _2.0.12:

2.0.12
======

- Fixed a TLS cipher listing issue.

.. _2.0.11:

2.0.11
======

- Fixed bug with TLS context not being passed to the socket listener.

.. _2.0.10:

2.0.10
======

- Added error catching to :py:obj:`socket.SO_REUSEPORT` -- on some systems this
  is available while still triggering a `Protocol Error` and causing blackhole
  to crash. The error catching will attempt to set this option if it's
  available but silently ignore it if it errors.

.. _2.0.9:

2.0.9
=====

- Added failsafe checks for IPv6 functionality. -- If you specify an IPv6
  listener but Python or the kernel have not been compiled with IPv6 support,
  an error will be returned.
- Moved out functionality for creating sockets and TLS contexts to separate
  control functions.
- Added warning for TLS being used with no Diffie Hellman ephemeral parameters
  being configured. -- :ref:`configuration-options`
- Added further security to TSL. The following options are now enforced.
  :py:obj:`ssl.OP_NO_COMPRESSION`, :py:obj:`ssl.OP_SINGLE_DH_USE`,
  :py:obj:`ssl.OP_SINGLE_ECDH_USE` and
  :py:obj:`ssl.OP_CIPHER_SERVER_PREFERENCE`.
  `See the Python documentation for more information on the flags
  <https://docs.python.org/3/library/ssl.html#ssl.OP_CIPHER_SERVER_PREFERENCE>`_.

.. _2.0.8:

2.0.8
=====

- Added IPv6 support.

.. _2.0.7:

2.0.7
=====

- Added email headers to SIZE checks. Resolves a potential DoS risk.

.. _2.0.6:

2.0.6
=====

- Enable or disable dynamic switches in configuration.

.. _2.0.5:

2.0.5
=====

- Fixed a bug with dynamic switches not being processed.

.. _2.0.4:

2.0.4
=====

- :ref:`dynamic-switches`.
- Re-added the ability to configure max message size. Displays in `EHLO` and
  enforced in `DATA` command. Default is 512000 bytes (512 KB).
- Added :ref:`tls_dhparams` options for loading Diffie Hellman ephemeral
  parameters.
- Added SMTP AUTH mechanisms. Currently PLAIN, LOGIN and CRAM-MD5 are
  supported.
- Added pidfile and related self tests to config_test command.

.. _2.0.3:

2.0.3
=====

No changes in particular except documentation changes. Tag was created
speficially for release to PyPI.

.. _2.0.2:

2.0.2
=====

- Added HELP verb that lists all available SMTP verbs. Sending
  ``HELP <COMMAND>`` will return the syntax for the specified command.

.. code-block:: none

    C: HELP
    S: 250 Supported commands: DATA EHLO ETRN HELO...
    C: HELP HELO
    S: 250 Syntax: HELO domain.tld
    C: HELP INVALID
    S: 501 Supported commands: DATA EHLO ETRN HELO...

- TLS settings changed based on format taken from
  `<https://docs.python.org/3/library/ssl.html#ssl-security>`_.
- TLS 'modern' ciphers enforced, ciphers taken from
  `<https://wiki.mozilla.org/Security/Server_Side_TLS>`_.

  .. code-block:: none

      0xC0,0x2C  -  ECDHE-ECDSA-AES256-GCM-SHA384  TLSv1.2  Kx=ECDH  Au=ECDSA  Enc=AESGCM(256)    Mac=AEAD
      0xC0,0x30  -  ECDHE-RSA-AES256-GCM-SHA384    TLSv1.2  Kx=ECDH  Au=RSA    Enc=AESGCM(256)    Mac=AEAD
      0xCC,0x14  -  ECDHE-ECDSA-CHACHA20-POLY1305  TLSv1.2  Kx=ECDH  Au=ECDSA  Enc=ChaCha20(256)  Mac=AEAD
      0xCC,0x13  -  ECDHE-RSA-CHACHA20-POLY1305    TLSv1.2  Kx=ECDH  Au=RSA    Enc=ChaCha20(256)  Mac=AEAD
      0xC0,0x2B  -  ECDHE-ECDSA-AES128-GCM-SHA256  TLSv1.2  Kx=ECDH  Au=ECDSA  Enc=AESGCM(128)    Mac=AEAD
      0xC0,0x2F  -  ECDHE-RSA-AES128-GCM-SHA256    TLSv1.2  Kx=ECDH  Au=RSA    Enc=AESGCM(128)    Mac=AEAD
      0xC0,0x24  -  ECDHE-ECDSA-AES256-SHA384      TLSv1.2  Kx=ECDH  Au=ECDSA  Enc=AES(256)       Mac=SHA384
      0xC0,0x28  -  ECDHE-RSA-AES256-SHA384        TLSv1.2  Kx=ECDH  Au=RSA    Enc=AES(256)       Mac=SHA384
      0xC0,0x23  -  ECDHE-ECDSA-AES128-SHA256      TLSv1.2  Kx=ECDH  Au=ECDSA  Enc=AES(128)       Mac=SHA256
      0xC0,0x27  -  ECDHE-RSA-AES128-SHA256        TLSv1.2  Kx=ECDH  Au=RSA    Enc=AES(128)       Mac=SHA256

.. _2.0.1:

2.0.1
=====

- Now **requires** Python 3.5 or above.
- Total refactoring. Now build on top of
  `asyncio <https://docs.python.org/3/library/asyncio.html>`_
  using
  `async def <https://docs.python.org/3/reference/compound_stmts.html#async-def>`_
  and `await <https://docs.python.org/3/reference/expressions.html#await>`_
  statements.
- Removed config options from command line args. Now only available in config
  file.
- Removed 'offline' and 'unavailable' modes.
- Refactored `init.d/debian-ubuntu/blackhole`, added `configtest` target.
- Removed reliance on all third party libraries.
- Removed deiman third party library and built it in.
- Debug flag no longer gives a warning.
- Delay flag is no longer a blocking method, now non-blocking and
  asynchronous.
- STARTTLS has been disabled, it's not available with :any:`asyncio`. -
  `https://bugs.python.org/review/23749/ <https://bugs.python.org/review/23749/>`_
- A lot of status codes have been removed.
