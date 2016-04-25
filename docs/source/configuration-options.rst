.. _configuration-options:

=====================
Configuration options
=====================

Here are all available options for the configuration file, their default values
and information on what the options actually do.

- `listen`_
- `tls_listen`_
- `user`_
- `group`_
- `pidfile`_
- `timeout`_
- `tls_cert`_
- `tls_key`_
- `tls_dhparams`_
- `delay`_
- `mode`_
- `max_message_size`_
- `dynamic_switch`_

-----

.. _listen:

listen
------

:Syntax:
    **listen** = *[address]:port, [address]:port*
:Default:
    listen=:25

`:25` is equivalent to listening on port 25 all IPv4 addresses and `:::25` is
equivalent to listening on port 25 on all IPv6 addresses.

Multiple addresses and ports can be listed on a single line.

::

    listen = 10.0.0.1:25, 10.0.0.2:25, :::25

-----

.. _tls_listen:

tls_listen
----------

:Syntax:
    **tls_listen** = *[address]:port, [address]:port*
:Default:
    Disabled

`:465` is equivalent to listening on port 465 all IPv4 addresses and `:::465` is
equivalent to listening on port 465 on all IPv6 addresses.

Multiple addresses and ports can be listed on a single line.

::

    tls_listen = 10.0.0.1:465, 10.0.0.2:465, :::465

-----

.. _user:

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

::

    user = blackhole

-----

.. _group:

group
-----

:Syntax:
    **group** = *group*
:Default:
    The primary group of the current Linux user

Blackhole will set it's process to the value provided with this options.

::

    group = blackhole

-----

.. _pidfile:

pidfile
-------

:Syntax:
    **pidfile** = */path/to/file.pid*
:Default:
    /tmp/blackhole.pid

Blackhole will write it's Process ID to this file, allowing you to easily track
the process and send signals to it.

::

    pidfile = /var/run/blackhole.pid

-----

.. _timeout:

timeout
-------

:Syntax:
    **timeout** = *secounds*
:Default:
    timeout=60. Maximum value of 180 seconds.

This is the amount of time to wait for a client to send data. Once the timeout
value has been reached with no data being sent by the client, the connection
will be terminated and a ``421 Timeout`` message will be sent to the client.

Helps mitigate DoS risks.

::

    timeout = 30

-----

.. _tls_cert:

tls_cert
--------

:Syntax:
    **tls_cert** = */path/to/certificate.pem*
:Default:
    None

The certificate file in x509 format for wrapping a connection in SSL/TLS.

::

    tls_cert = /etc/ssl/certs/blackhole.crt

-----

.. _tls_key:

tls_key
-------

:Syntax:
    **tls_key** = */path/to/private.key*
:Default:
    None

The private key of the `tls_cert`_.

::

    tls_key = /etc/ssl/private/blackhole.key

-----

.. _tls_dhparams:

tls_dhparams
------------

:Syntax:
    **tls_dhparams** = */path/to/dhparams.pem*
:Default:
    None

File containing Diffie Hellman ephemeral parameters for ECDH ciphers.

::

    tls_dhparams = /etc/ssl/dhparams.pem

-----

.. _delay:

delay
-----

:Syntax:
    **delay** = *secounds*
:Default:
    Disabled. Maximum value of 60 seconds.

Time to delay before returning a response to a completed DATA command. You can
use this to delay testing or simulate lag.

::

    delay = 30

-----

.. _mode:

mode
----

:Syntax:
    **mode** = *accept | bounce | random*
:Default:
    accept -- valid options are:- accept, bounce, random.

::

    mode = random

-----

.. _max_message_size:

max_message_size
----------------

:Syntax:
    **max_message_size** = *bytes*
:Default:
    512000 Bytes (512 KB)

The maximum message size for a message. This includes headers and helps
mitigate a DoS risk.

::

    max_message_size = 1024000

-----

.. _dynamic_switch:

dynamic_switch
--------------

:Syntax:
    **dynamic_switch** = *true | false*
:Default:
    true -- valid options are:- true, false.

The dynamic switch option allows you to enable or disable parsing of dynamic
switches from email headers -- :ref:`dynamic-switches`

::

    dynamic_switch = false
