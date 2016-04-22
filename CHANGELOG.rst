.. _changelog:

=========
Changelog
=========

Upcoming/planned features
=========================

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

2.0.4
=====

- Re-added the ability to configure max message size. Displays in EHLO and is
  enforced in DATA command. Default is 512000 bytes (512 KB).
- Added `tls_dhparams` options for loading Diffie Hellman ephemeral parameters.
- Added SMTP AUTH mechanisms. Currently PLAIN, LOGIN and CRAM-MD5 are
  supported.

2.0.3
=====

No changes in particular except documentation changes. Tag was created
speficially for release to PyPI.

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
- STARTTLS has been disabled, it's not available with `asyncio`. -
  `https://bugs.python.org/review/23749/ <https://bugs.python.org/review/23749/>`_
- A lot of status codes have been removed.

1.8.1
=====

- Added message_size_limit configuration flag to modify the EHLO 205-SIZE
  output. Some clients read this value and evaluate the message they're
  sending to the server and refuse to send it due to the message size being
  larger than the default limit.
  This limit is not enforced by the server itself.

1.8.0
=====

- Removed bin/blackhole and replaced it with a Python entry point
- Cleaned up the source code and modified error checking
- Major refactoring of tests
- Added a requirement of the mock libary to run tests
- Added a wealth of tests for many new methods and some old ones that were
  absent
- Changed get_mailname method to use `__builtin__.open` instead of
  `__builtin__.file`

1.7.0
=====

- Added STARTTLS

1.6.4
=====

- Added delay flag
- Fixed daemonisation issue on PyPy
- Added FQDN to HELO/EHLO
- Removed SMTP 251-253 from responses

1.6.0
=====

- Python 3
- Deprecate ssl_ca_certs_dir
