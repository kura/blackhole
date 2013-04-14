"""blackhole.opts - command line options for the blackhole
server.

Also creates a list of available ports for the server to be
run on, based on configuration and responds with the help
menu when requested or invalid options are given."""

import sys

from tornado.options import define, options

from blackhole import __pname__, __fullname__


define('workers', default=None, metavar="NUM", type=int,
       help="Number of worker processes to spawn. (default: # of CPUs/Cores + 1 master)",
       group="Blackhole")
define('host', default="0.0.0.0", metavar="IP", type=str,
       help="IP address to bind go",
       group="Blackhole")
define('port', default=25, metavar="PORT", type=int,
       help="Port to listen for connections on",
       group="Blackhole")
define('pid', default="/tmp/blackhole.pid", metavar="FILE", type=str,
       help="File to write process information to",
       group="Blackhole")
define("conf", metavar="FILE",
       help="Config file to parse and use. Overrides command line args",
       group="Blackhole")
define("user", default="blackhole",
       metavar="USER", help="User to drop privs to during run time",
       group="Blackhole")
define("group", default="blackhole",
       metavar="GROUP", help="Group to drop privs to during run time",
       group="Blackhole")
define("log", default="/tmp/blackhole.log",
       metavar="FILE", help="File to write logs to (not very verbose)",
       group="Blackhole")

define('debug', default=False, metavar="BOOL", type=bool,
       help="Enable/disable debug logging mode. Causes a lot of disk I/O",
       group="Debug")

define("mode", default="accept",
       metavar="MODE", help="Mode to run blackhole in (accept, bounce, random,\n%-37sunavailable, offline)" % "",
       group="Mode")

define('ssl', default=True, metavar="BOOL", type=bool,
       help="Enable/disable SSL",
       group="Blackhole SSL")
define('ssl_port', default=465, metavar="PORT", type=int,
       help="Port to listen for SSL connections on",
       group="Blackhole SSL")
define('ssl_cert', default=None, metavar="PATH", type=str,
       help="SSL Certificate",
       group="Blackhole SSL")
define('ssl_key', default=None, metavar="PATH", type=str,
       help="SSL Private Key",
       group="Blackhole SSL")
define('ssl_ca_certs_dir', default="/etc/ssl/certs/", metavar="PATH", type=str,
       help="SSL CA Certificates directory",
       group="Blackhole SSL")

# Eugh, had to replicate to shut up Tornado..
define('version', default=True,
       help="Return program version")
define('v', default=True,
       help="Return program version")


def ports():
    """
    Create and return a list of sockets we need to create.

    A maximum of two will be returned, default is standard
    (std) and SSL (ssl) it is enabled.
    """
    socks_list = ['std']
    if options.ssl:
        socks_list.append('ssl')
    return socks_list


def print_help(afile=None):
    """Prints all the command line options to stdout."""
    afile = sys.stdout
    print >> afile, "Usage: %s [OPTIONS] (start|stop|status)" % (__pname__)
    print >> afile
    print >> afile, "  -v, --%-26s %s" % ("version", "Print out program version")
    print >> afile, "  -h, --%-26s %s" % ("help", "Show this help information")
    by_group = {}
    opts = {}
    for option, value in options._options.iteritems():
        # hack to bypass Tornado options
        if option.startswith(("workers", "host", "port", "pid",
                              "conf", "user", "group", "log",
                              "debug", "mode", "ssl",
                              "ssl_port", "ssl_cert", "ssl_key",
                              "ssl_ca_certs_dir")):
            if not option.startswith(("log_", "logging")):
                opts[option] = value
    for option in opts.itervalues():
        by_group.setdefault(option.group_name, []).append(option)

    for filename, o in sorted(by_group.items()):
        if filename and not filename.endswith("log.py"):
            print >> afile
            print >> afile, filename
            l = ""
            for _ in xrange(0, len(filename)):
                l += "-"
            print >> afile, l
            print >> afile
        o.sort(key=lambda option: option.name)
        for option in o:
            prefix = option.name
            if option.metavar:
                prefix += "=" + option.metavar
            print >> afile, "  --%-30s %s" % (prefix, option.help or "")
            if option.name == "mode":
                print >> afile
                print >> afile, "%-34s accept - accept all email with code 250, 251, 252 or 253" % ""
                print >> afile, "%-34s bounce - bounce all email with a random code,\n%-37sexcluding 250, 251, 252, 253" % ("", "")
                print >> afile, "%-34s random - randomly accept or bounce all email with a random code" % ""
                print >> afile, "%-34s unavailable - server always respondes with code 421\n%-37s- service is unavailable" % ("", "")
                print >> afile, "%-34s offline - server always responds with code 521 - server\n%-37sdoes not accept mail" % ("", "")
    print >> afile
