=========
Blackhole
=========

Tornado powered MTA for accepting all incoming emails 
without any disk I/O, although no messages actually ever 
get delivered. 
Mainly for testing huge send rates, for making sure developers
don't accidentally send emails to real users, email
integration testing and things like that.


Requirements
------------

* tornado 2.3
* setproctitle 1.1.6


Installation
------------

Packaged
~~~~~~~~

From PyPI

  pip install blackhole

Or

  easy_install blackhole

From GitHub
~~~~~~~~~~~

  pip install -e git+git://github.com/kura/blackhole.git#egg=blackhole

From source
~~~~~~~~~~~

Download the latest tarball from PyPI or GitHub. Unpack and run:

  python setup.py install


Configuration
-------------

Configuration options can be passed via the command line
as below:

  --host=IP					IP address to bind go [default: 0.0.0.0]
  --port=PORT				Port to listen for connections on [default: 25]
  --pid=FILE				File to write process information to [default: /tmp/blackhole.pid]
  --log=FILE				File to write logs to (not very verbose) [default: /tmp/blackhole.log]
  --user=USER				User to drop privs to during run time. [default: blackhole]
  --group=GROUP			Group to drop privs to during run time. [default: blackhole]
  --mode=MODE				Mode to run blackhole in (accept, bounce, random, unavailable, offline) [default: accept] - see MODES section

SSL options

  --ssl=BOOL										Enabled or disable SSL, requires SSL compiled in to Python and OpenSSL. True or False [default: True]
  --ssl_port=PORT								Port to listen for SSL enabled connections [default: 465]
  --ssl_key=PATH								X509 SSL keyfile
  --ssl_cert=PATH								X509 SSL certificate file
  --ssl_ca_certs_dir=PATH				Path to your operating system's repository of certificates authorities [default: /etc/ssl/certs]


You can also specify the `--conf` option to load configuration
from a file:

  --conf=FILE		Config file to parse and use. Overrides command line args

The configuration file has the following format::

  host="0.0.0.0"
  port=25
  pid="/tmp/blackhole.io"
  mode="offline"
  ssl_key=/etc/ssl/private/blackhole.io.key
  ssl_cert=/etc/ssl/certs/blackhole.io.crt

You can find an example configuration file `example.conf-dist` in the root folder of this project.


Usage
-----

Using the blackhole binary
~~~~~~~~~~~~~~~~~~~~~~~~~~

The following commands are for use when using blackhole without an init script.

+-------------------+----------------------------------------------------------+
| blackhole start   | Starts the server                                        |
+-------------------+----------------------------------------------------------+
| blackhole stop    | Stops the server                                         |
+-------------------+----------------------------------------------------------+
| blackhole restart | Restarts the server                                      |
+-------------------+----------------------------------------------------------+
| blackhole status  | Shows the status of the server, running, not running etc |
+-------------------+----------------------------------------------------------+

Using init.d
~~~~~~~~~~~~

Please see the section below on installing the init.d/rc.d script.

+-------------------------------+----------------------------------------------------------+
| /etc/init.d/blackhole start   | Starts the server                                        |
+-------------------------------+----------------------------------------------------------+
| /etc/init.d/blackhole stop    | Stops the server                                         |
+-------------------------------+----------------------------------------------------------+
| /etc/init.d/blackhole restart | Restarts the server                                      |
+-------------------------------+----------------------------------------------------------+
| /etc/init.d/blackhole status  | Shows the status of the server, running, not running etc |
+-------------------------------+----------------------------------------------------------+

Modes
-----

See the `Response codes` section for more information on responses
and which mode responds with which codes.

accept
~~~~~~

Accept all email with code 250, 251, 252 or 253.

bounce
~~~~~~

Bounce all email with a random code, excluding 250, 251, 252, 253.

random
~~~~~~

Randomly accept or bounce all email with a random code.

unavailable
~~~~~~~~~~~

Server always respondes with code 421 - service is unavailable.

offline
~~~~~~~


Server always responds with code 521 - server does not accept mail.

rc.d
----

The init script depends on */etc/blackhole.conf* being in place and configured, see README
section on configuration.

Blackhole comes with a script that works with init.d/rc.d, to install it copy it
from the *init.d/YOUR_DISTRO* folder in the root directory of this project to */etc/init.d/*.

i.e. for Debian/Ubuntu users, mv the file from *init.d/debian-ubuntu/* to */etc/init.d/*.

Then make sure it's executable::

  chmod +x /etc/init.d/blackhole

To make blackhole start on a reboot use the following::

  update-rc.d blackhole defaults


Response codes
--------------

All
~~~

+------+------------------------------------------------------------+
| Code | message                                                    |
+======+============================================================+
| 220  | OK, ready                                                  |
+------+------------------------------------------------------------+
| 221  | Thank you for speaking to me                               |
+------+------------------------------------------------------------+
| 250  | OK, done                                                   |
+------+------------------------------------------------------------+
| 251  | OK, user not local, will forward                           |
+------+------------------------------------------------------------+
| 252  | OK, cannot VRFY user but will attempt delivery             |
+------+------------------------------------------------------------+
| 253  | OK, messages pending                                       |
+------+------------------------------------------------------------+
| 354  | Start mail input; end with <CRLF>.<CRLF>                   |
+------+------------------------------------------------------------+
| 355  | Octet-offset is the transaction offset                     |
+------+------------------------------------------------------------+
| 421  | Service not available, closing transmission channel        |
+------+------------------------------------------------------------+
| 450  | Requested mail action not taken: mailbox unavailable       |
+------+------------------------------------------------------------+
| 451  | Requested action aborted: local error in processing        |
+------+------------------------------------------------------------+
| 452  | Requested action not taken: insufficient system storage    |
+------+------------------------------------------------------------+
| 454  | TLS not available due to temporary reason                  |
+------+------------------------------------------------------------+
| 458  | Unable to queue message                                    |
+------+------------------------------------------------------------+
| 459  | Not allowed: unknown reason                                |
+------+------------------------------------------------------------+
| 500  | Command not recognized                                     |
+------+------------------------------------------------------------+
| 501  | Syntax error, no parameters allowed                        |
+------+------------------------------------------------------------+
| 502  | Command not implemented                                    |
+------+------------------------------------------------------------+
| 503  | Bad sequence of commands                                   |
+------+------------------------------------------------------------+
| 504  | Command parameter not implemented                          |
+------+------------------------------------------------------------+
| 521  | Machine does not accept mail                               |
+------+------------------------------------------------------------+
| 530  | Must issue a STARTTLS command first                        |
+------+------------------------------------------------------------+
| 534  | Authentication mechanism is too weak                       |
+------+------------------------------------------------------------+
| 538  | Encryption required for requested authentication mechanism |
+------+------------------------------------------------------------+
| 550  | Requested action not taken: mailbox unavailable            |
+------+------------------------------------------------------------+
| 551  | User not local                                             |
+------+------------------------------------------------------------+
| 552  | Requested mail action aborted: exceeded storage allocation |
+------+------------------------------------------------------------+
| 553  | Requested action not taken: mailbox name not allowed       |
+------+------------------------------------------------------------+
| 554  | Transaction failed                                         |
+------+------------------------------------------------------------+
| 571  | Blocked                                                    |
+------+------------------------------------------------------------+

Accept
~~~~~~

This mode will respond with the following codes:

+-------------------------+
| Codes                   |
+=======+=====+=====+=====+
| 250   | 251 | 252 | 253 |
+-------+-----+-----+-----+

Bounce
~~~~~~

This mode will respond with the following codes:

+-------------------------------------------------+
| Codes                                           |
+=======+=====+=====+=====+=====+=====+=====+=====+
| 421   | 431 | 450 | 451 | 452 | 454 | 458 | 459 |
+-------+-----+-----+-----+-----+-----+-----+-----+
| 521   | 534 | 550 | 551 | 552 | 553 | 554 | 571 |
+-------+-----+-----+-----+-----+-----+-----+-----+

Offline
~~~~~~~

This mode will respond with the following codes:

+-------+
| Codes |
+=======+
| 521   |
+-------+

Unavailable
~~~~~~~~~~~

This mode will respond with the following codes:

+-------+
| Codes |
+=======+
| 421   |
+-------+
