=========
Blackhole
=========

Tornado powered MTA for accepting all incoming emails 
without any disk I/O, although no messages actually ever 
get delivered. 
Mainly for testing huge send rates, for making sure developers
don't accidentally send emails to real users, email
integration testing and things like that


Requirements
------------

* tornado 2.3
* setproctitle 1.1.6


Installation
------------

  python setup.py install


Configuration
-------------

Configuration options can be passed via the command line
as below

  --host=IP			IP address to bind go [default: 0.0.0.0]
  --port=PORT		Port to listen for connections on [default: 25]
  --pid=FILE		File to write process information to [default: /tmp/blackhole.pid]
  --log=FILE 		File to write logs to (not very verbose) [default: /tmp/blackhole.log]
  --user=USER		User to drop privs to during run time. [default: blackhole]
  --group=GROUP		Group to drop privs to during run time. [default: blackhole]


You can also specify the `--conf` option to load configuration
from a file

  --conf=FILE		Config file to parse and use. Overrides command line args

The configuration file has the following format::

  host="0.0.0.0"
  port=25
  pid="/tmp/blackhole.io"


Usage
-----

  blackhole start		Starts the server

  blackhole stop		Stops the server

  blackhole Restarts	Restarts the server

  blackhole status		Shows the status of the server, running, not running etc
