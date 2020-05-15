================
blackhole_config
================

--------------------------------------------
the config file format for the Blackhole MTA
--------------------------------------------

:Manual section: 1

DESCRIPTION
===========

This manual page documents the ``Blackhole`` configuration file format and
options.

OPTIONS
=======

These are all available options for the configuration file, their default
values and information on what the options actually do.

The file format is a simple `attribute = value` style, an example is shown
below.

::

    # This is a comment.
    listen = :25  # This is an inline comment.
    user = kura
    group = kura

listen
------

:Syntax:
    **listen** = *[address]:port [mode=MODE] [delay=DELAY]*
:Default:
    127.0.0.1:25, 127.0.0.1:587, :::25, :::587 -- 25 is the recognised SMTP
    port, 587 is the recognised SMTP Submission port. IPv6 listeners are only
    enabled if IPv6 is supported.
:Optional:
    *mode=* and *delay=* -- allows setting a response mode and delay per
    listener.

`:25` is equivalent to listening on port 25 on all IPv4 addresses and `:::25`
is equivalent to listening on port 25 on all IPv6 addresses.

Multiple addresses and ports can be listed on a single line.

::

    listen = 10.0.0.1:25, 10.0.0.2:25, :25, :::25, :587, :::587

The ``mode=`` and ``delay=`` flags allow specific ports to act in specific
ways. i.e. you could accept all mail on 10.0.0.1:25 and bounce it all on
10.0.0.2:25, as below.

::

    listen = 10.0.0.1:25 mode=accept, 10.0.0.2:25 mode=bounce

The ``mode=`` and ``delay=`` flags may also be specified together, as required.

::

    listen = 10.0.0.1:25 mode=accept delay=5, 10.0.0.2:25 mode=bounce delay=10

The flags accept the same options as `dynamic-switches`, including setting
a delay range.

-----

tls_listen
----------

:Syntax:
    **tls_listen** = *[address]:port [mode=MODE] [delay=DELAY]*
:Default:
    None -- 465 is the recognised SMTPS port [1]_.
:Optional:
    *mode=* and *delay=* -- allows setting a response mode and delay per
    listener.
:Added:

`:465` is equivalent to listening on port 465 on all IPv4 addresses and
`:::465` is equivalent to listening on port 465 on all IPv6 addresses.

Multiple addresses and ports can be listed on a single line.

::

    tls_listen = 10.0.0.1:465, 10.0.0.2:465, :465, :::465

The ``mode=`` and ``delay=`` flags allow specific ports to act in specific
ways. i.e. you could accept all mail on 10.0.0.1:465 and bounce it all on
10.0.0.2:465, as below.

::

    tls_listen = 10.0.0.1:465 mode=accept, 10.0.0.2:465 mode=bounce

The ``mode=`` and ``delay=`` flags may also be specified together, as required.

::

    tls_listen = 10.0.0.1:465 mode=accept delay=5, 10.0.0.2:465 mode=bounce delay=10

The flags accept the same options as `dynamic-switches`, including setting
a delay range.

.. [1] Port 465 -- while originally a recognised port for SMTP over
   SSL/TLS -- is no longer advised for use. It's listed here because it's a
   well known and well used port, but also because Blackhole currently does not
   support ``STARTTLS`` over SMTP or SMTP Submission. --
   `<https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.txt>`_

-----

user
----

:Syntax:
    **user** = *user*
:Default:
    The current Linux user

Blackhole will set it's process owner to the value provided with this options.
Ports below 1024 require sudo or root privileges, this option is available so
that the process can be started, listen on privileged ports and then give up
those privileges.

-----

group
-----

:Syntax:
    **group** = *group*
:Default:
    The primary group of the current Linux user

Blackhole will set it's process group to the value provided with this options.

-----

pidfile
-------

:Syntax:
    **pidfile** = */path/to/file.pid*
:Default:
    /tmp/blackhole.pid

Blackhole will write it's Process ID to this file, allowing you to easily track
the process and send signals to it.

-----

timeout
-------

:Syntax:
    **timeout** = *seconds*
:Default:
    60 -- Maximum value of 180 seconds.

This is the amount of time to wait for a client to send data. Once the timeout
value has been reached with no data being sent by the client, the connection
will be terminated and a ``421 Timeout`` message will be sent to the client.

Helps mitigate DoS risks.

-----

tls_cert
--------

:Syntax:
    **tls_cert** = */path/to/certificate.pem*
:Default:
    None

The certificate file in x509 format for wrapping a connection in SSL/TLS.

-----

tls_key
-------

:Syntax:
    **tls_key** = */path/to/private.key*
:Default:
    None

-----

tls_dhparams
------------

:Syntax:
    **tls_dhparams** = */path/to/dhparams.pem*
:Default:
    None


File containing Diffie Hellman ephemeral parameters for ECDH ciphers.

-----

delay
-----

:Syntax:
    **delay** = *seconds*
:Default:
    None -- Maximum value of 60 seconds.

Time to delay before returning a response to a completed DATA command. You can
use this to delay testing or simulate lag.

-----

mode
----

:Syntax:
    **mode** = *accept | bounce | random*
:Default:
    accept

-----

max_message_size
----------------

:Syntax:
    **max_message_size** = *bytes*
:Default:
    512000 Bytes (512 KB)

The maximum message size for a message. This includes headers and helps
mitigate a DoS risk.

-----

dynamic_switch
--------------

:Syntax:
    **dynamic_switch** = *true | false*
:Default:
    true

The dynamic switch option allows you to enable or disable parsing of dynamic
switches from email headers.

-----

workers
-------

:Syntax:
    **workers** = *number*
:Default:
    1

The workers option allows you to define how many worker processes to spawn to
handle incoming mail. The absolute minimum is actually 2. Even by setting the
``workers`` value to 1, a supervisor process will always exist meaning that you
would have 1 worker and a supervisor.

SEE ALSO
========

- **blackhole** (1)
- `<https://kura.github.io/blackhole/configuration.html>`_

LICENSE
=======

The MIT license must be distributed with this software.

AUTHOR(S)
=========

Kura <kura@kura.gg>
