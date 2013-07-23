.. _configuration_options:

=====================
Configuration options
=====================

Configuration options can be passed via the command line
as below:

  --workers=NUM					Number of child workers to spawn (default: # of CPUs/cores + 1 master)
  --host=IP					IP address to bind go (default: 0.0.0.0)
  --port=PORT					Port to listen for connections on (default: 25)
  --pid=FILE					File to write process information to (default: /tmp/blackhole.pid)
  --log=FILE					File to write logs to (not very verbose) (default: /tmp/blackhole.log)
  --user=USER					User to drop privs to during run time. (default: blackhole)
  --group=GROUP					Group to drop privs to during run time. (default: blackhole)
  --mode=MODE					Mode to run blackhole in (accept, bounce, random, unavailable, offline) (default: accept) - see :ref:`modes` section
  --debug=BOOL					Will set the debug flag and causes all received and sent command/email data to be logged. Will degrade performance with high throughput (default: False)
  --delay=SECONDS				Will set the delay flag and cause the server to wait X seconds before responding. (default: 0)

SSL options

  --ssl=BOOL					Enabled or disable SSL, requires SSL compiled in to Python and OpenSSL. True or False (default: True)
  --ssl_port=PORT				Port to listen for SSL enabled connections (default: 465)
  --ssl_key=PATH				X509 SSL keyfile
  --ssl_cert=PATH				X509 SSL certificate file


You can also specify the `--conf` option to load configuration
from a file:

  --conf=FILE					Config file to parse and use. Overrides command line args

For more information on the configuration file format read :ref:`configuration_file_example`.

Deprecated options
------------------

The following options are deprecated and should not be used.

  --ssl_ca_certs_dir=PATH			Path to your operating system's repository of certificates authorities (default: None)
