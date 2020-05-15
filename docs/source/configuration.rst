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

=============
Configuration
=============

.. _command-line-options:

Command line options
====================

Configuration options can be passed via the command line
as below:

-h			show this help message and exit
-v			show program's version number and exit
-c FILE		override the default configuration options
-t			perform a configuration test and exit
-d			enable debugging mode
-b			run in the background
-ls			Disable :py:obj:`ssl.OP_SINGLE_DH_USE` and :py:obj:`ssl.OP_SINGLE_ECDH_USE`.
			Reduces CPU overhead at the expense of security. Don't use this
			option unless you really need to. -- added in :ref:`2.0.13`
-q			Suppress warnings when using -ls/--less-secure, running as root or
			not using :ref:`tls_dhparams` option.


.. _configuration-options:

Configuration options
=====================

Here are all available options for the configuration file, their default values
and information on what the options actually do.

From :ref:`2.1.8` onwards the ``blackhole_config`` command will also display this
information directly from the command line.

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
- `workers`_

-----

.. _listen:

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
:Added:
    :ref:`2.0.8` -- introduced the new IPv6 aware syntax
    :ref:`2.1.4` -- added optional mode and delay flags

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

The flags accept the same options as :ref:`dynamic-switches`, including setting
a delay range.

-----

.. _tls_listen:

tls_listen
----------

:Syntax:
    **tls_listen** = *[address]:port [mode=MODE] [delay=DELAY]*
:Default:
    None -- 465 is the recognised SMTPS port [*]_.
:Optional:
    *mode=* and *delay=* -- allows setting a response mode and delay per
    listener.
:Added:
    :ref:`2.0.8` -- introduced the new IPv6 aware syntax
    :ref:`2.1.4` -- added optional mode and delay flags

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

The flags accept the same options as :ref:`dynamic-switches`, including setting
a delay range.

.. [*] Port 465 -- while originally a recognised port for SMTP over
   SSL/TLS -- is no longer advised for use. It's listed here because it's a
   well known and well used port, but also because Blackhole currently does not
   support ``STARTTLS`` over SMTP or SMTP Submission. --
   `<https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.txt>`_

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

Blackhole will set it's process group to the value provided with this options.

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
:Added:
    :ref:`2.0.4`

Blackhole will write it's Process ID to this file, allowing you to easily track
the process and send signals to it.

::

    pidfile = /var/run/blackhole.pid

-----

.. _timeout:

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
:Added:
    :ref:`2.0.4`


File containing Diffie Hellman ephemeral parameters for ECDH ciphers.

::

    tls_dhparams = /etc/ssl/dhparams.pem

-----

.. _delay:

delay
-----

:Syntax:
    **delay** = *seconds*
:Default:
    None -- Maximum value of 60 seconds.

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
:Added:
    :ref:`2.0.4`

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
:Added:
    :ref:`2.0.6`

The dynamic switch option allows you to enable or disable parsing of dynamic
switches from email headers -- :ref:`dynamic-switches`

::

    dynamic_switch = false

-----

.. _workers:

workers
-------

:Syntax:
    **workers** = *number*
:Default:
    1
:Added:
    :ref:`2.1.0`

The workers option allows you to define how many worker processes to spawn to
handle incoming mail. The absolute minimum is actually 2. Even by setting the
``workers`` value to 1, a supervisor process will always exist meaning that you
would have 1 worker and a supervisor.

-----


STARTTLS
--------

Currently `asyncio` does not have the code in place to make STARTTLS
possible, the STARTTLS verb returns a ``500 Not implemented`` response
until it's possible to implement. --`https://bugs.python.org/review/23749/
<https://bugs.python.org/review/23749/>`_


Optional features (you should probably use)
===========================================

Blackhole has builtin support for the following features. While these are not
required for the service to run, they do improve it the server in various ways.

uvloop
------

    uvloop is a fast, drop-in replacement of the built-in asyncio event loop.
    uvloop is implemented in Cython and uses libuv under the hood.

Using `uvloop <https://github.com/MagicStack/uvloop>`_ with Blackhole is as
simple as installing `libuv <https://github.com/libuv/libuv>`_ and the
Blackhole extra package.

On Debian/Ubuntu it's as simple as installing via APT and Pip respectively.

.. code:: bash

    apt-get install libuv1 libuv1-dev python-dev
    pip install blackhole[uvloop]

setproctitle
------------

`setproctitle <https://pypi.python.org/pypi/setproctitle>`_ is a simple library
that allows Blackhole to set a more `ps aux`-friendly output for the blackhole
processes.

.. code:: bash

    # without setproctitle
    python3.6 /home/kura/.virtualenvs/blackhole/bin/blackhole -c test.conf -d
    python3.6 /home/kura/.virtualenvs/blackhole/bin/blackhole -c test.conf -d
    # with setproctitle
    blackhole: master
    blackhole: worker

You can install setproctitle with the Blackhole extra package.

.. code:: bash

    pip install blackhole[setproctitle]


Installing the init.d/rc.d scripts
==================================

The init script depends on */etc/blackhole.conf* being in place and configured.

Blackhole comes with a script that works with init.d/rc.d, to install it copy it
from the *init.d/YOUR_DISTRO* folder in the root directory of this project to
*/etc/init.d/*.

The init scripts can be found `here`_.

.. _here: https://github.com/kura/blackhole/tree/master/init.d

i.e. for Debian/Ubuntu users, mv the file from *init.d/debian-ubuntu/* to */etc/init.d/*.

Then make sure it's executable

.. code-block:: bash

  chmod +x /etc/init.d/blackhole

To make blackhole start on a reboot use the following::

  update-rc.d blackhole defaults
