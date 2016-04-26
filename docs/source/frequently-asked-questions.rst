.. _frequently-asked-questions:

==========================
Frequently asked questions
==========================

Here are some of the questions most frequently asked.

#. `Which ports should I open or use?`_
#. `What are the default configuration values?`_
#. `Is IPv6 supported?`_
#. `What are the permissions required for running the server?`_
#. `Why is SMTPS supported but STARTTLS is not?`_
#. `What encryption, security methodologies and practices are in place?`_

Which ports should I open or use?
=================================

Below is a list of the commonly used ports for SMTP.

+------+--------------------+
| Port |                    |
+======+====================+
| 25   | SMTP               |
+------+--------------------+
| 587  | SMTP Submission    |
+------+--------------------+
| 465  | SMTP SSL/TLS [*]_  |
+------+--------------------+

.. [*] Port 465 -- while originally a recognised port for SMTP over
   SSL/TLS -- is no longer advised for use. It's listed here because it's a
   well known and well used port, but also because Blackhole currently does not
   support ``STARTTLS`` over SMTP or SMTP Submission. --
   `<https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.txt>`_

What are the default configuration values?
==========================================

Unless told otherwise, blackhole will attempt to load it's configuration from:

.. code-block:: ini

    /etc/blackhole.conf

The following options are default, even if no configuration is passed at
runtime:

.. code-block:: ini

    listen=127.0.0.1:25
    timeout=60

Is IPv6 supported?
==================

Yes. IPv6 is supported alongside IPv4 in both the ``listen`` and ``tls_listen``
arguments. IPv6 and IPv4 listeners can be configured together.

.. code-block:: ini

    listen=0.0.0.0:25, :::25
    tls_listen=0.0.0.0:465, :::465

What are the permissions required for running the server?
=========================================================

By default blackhole runs as the current user and group.

On Linux all ports below and including port 1023 require `sudo` or `root`
privileges. -- blackhole is no different. To combat this issue, a lower
privilige user and group can be specified in the configuration.

Blackhole will start listening on the privileged ports before dropping
privileges for security.

Why is SMTPS supported but STARTTLS is not?
===========================================

Currently the ``asyncio`` library in the Python standard library does not
support the mechanisms required to implement `STARTTLS`. The technical reason
for this is that when asyncio was added to the standard library the
``ssl.MemoryBIO`` had not been included and so wrapping the
``asyncio.StreamReader`` and ``asyncio.StreamWriter`` in an SSL/TLS context
is not possible. A patch is waiting to be included at a future date. --
`<https://bugs.python.org/review/23749/>`_

What encryption, security methodologies and practices are in place?
===================================================================

Blackhole supports `TLSv1.2` only, `SSLv3` and `SSLv2` are explicitly disabled.
SSL/TLS compression is also disabled and ``OP_SINGLE_DH_USE`` and
``OP_SINGLE_ECDH_USE`` are also enforced. These two options prevent the same
Diffie Hellman and Elliptic Curve Diffie Hellman keys from being re-used for
distinct sessions.

The ``OP_CIPHER_SERVER_PREFERENCE`` flag is also set, during the SSL/TLS
handshake the server will tell the client to respect the server's order
of cipher suites.

The following ciphers are enabled.

.. code-block:: ini

    ECDHE-ECDSA-AES256-GCM-SHA384
    ECDHE-RSA-AES256-GCM-SHA384
    ECDHE-ECDSA-CHACHA20-POLY1305
    ECDHE-RSA-CHACHA20-POLY1305
    ECDHE-ECDSA-AES128-GCM-SHA256
    ECDHE-RSA-AES128-GCM-SHA256
    ECDHE-ECDSA-AES256-SHA384
    ECDHE-RSA-AES256-SHA384
    ECDHE-ECDSA-AES128-SHA256
    ECDHE-RSA-AES128-SHA256

There is also a configuration option -- ``tls_dhparams`` --  allowing loading
the key generation parameters for Diffie-Helman key exchange, improving forward
secrecy.

Blackhole also does not allow random user data. All commands are confined and
controlled. Where user data acceptance is more fluid, like the ``DATA``
command, the user-provided data is not executed, it is simply thrown away.
