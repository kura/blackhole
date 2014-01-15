# (The MIT License)
#
# Copyright (c) 2013 Kura
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

"""
blackhole.opts - command line options for the blackhole
server.

Also creates a list of available ports for the server to be
run on, based on configuration and responds with the help
menu when requested or invalid options are given.
"""

try:
    import ssl
except ImportError:
    ssl = None

from tornado.options import (define, options)
from tornado import process

from blackhole import __pname__

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
define("message_size_limit", default=512000, metavar="BYTES", type=int,
       help="""Maximum size of a message in Bytes, returned in EHLO but"""
            """\n%-37snot enforced""" % "",
       group="Blackhole")

define('workers', default=None, metavar="NUM", type=int,
       help="""Number of worker processes to spawn."""
            """(default: # of CPUs/Cores - 2 + 1 master)""",
       group="Workers")

define('debug', default=False, metavar="BOOL", type=bool,
       help="Enable/disable debug logging mode. Causes a lot of disk I/O",
       group="Debug")

define('delay', default=0, metavar="INT", type=int,
       help="Delay SMTP connection for number of seconds passed",
       group="Delay")

define("mode", default="accept",
       metavar="MODE", help="""Mode to run blackhole in (accept, bounce, """
                            """random,\n%-37sunavailable, offline)""" % "",
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
define('ssl_ca_certs_dir', default=None, metavar="PATH", type=str,
       help="SSL CA Certificates directory",
       group="Blackhole SSL")

# Eugh, had to replicate to shut up Tornado..
define('version', help="Return program version")
define('v', help="Return program version")


def ports():
    """
    Create and return a list of sockets we need to create.

    A maximum of two will be returned, default is standard
    (std) and SSL (ssl) it is enabled.
    """
    socks_list = ['std']
    # We shouldn't be able to create an SSL socket if it's
    # disabled or if there's non SSL libary
    if options.ssl and ssl:
        socks_list.append('ssl')
    return socks_list


def workers():
    if options.workers is None:
        return process.cpu_count() - 2
    return options.workers


def deprecated_opts():
    dep = ('ssl_ca_certs_dir', )
    for d in dep:
        if getattr(options, d) is not None:
            print("Deprecated option: %s" % d)


def print_help():
    """Prints all the command line options to stdout."""
    print("Usage: %s [OPTIONS] (start|stop|status)" % (__pname__))
    print("")
    print("  -v, --%-26s %s" % ("version", "Print out program version"))
    print("  -h, --%-26s %s" % ("help", "Show this help information"))
    by_group = {}
    opts = {}
    for option, value in options._options.items():
        # hack to bypass Tornado options
        if option.startswith(("workers", "host", "port", "pid",
                              "conf", "user", "group", "log",
                              "debug", "delay", "mode", "ssl",
                              "ssl_port", "ssl_cert", "ssl_key",
                              "message_size_limit")):
            if not option.startswith(("log_", "logging", "ssl_ca_certs_dir")):
                opts[option] = value
    for option in opts.values():
        by_group.setdefault(option.group_name, []).append(option)

    for filename, o in sorted(by_group.items()):
        if filename and not filename.endswith("log.py"):
            print("")
            print(filename)
            l = ""
            for _ in range(0, len(filename)):
                l += "-"
            print(l)
            print("")
        o.sort(key=lambda option: option.name)
        for option in o:
            prefix = option.name
            if option.metavar:
                prefix += "=" + option.metavar
            print("  --%-30s %s" % (prefix, option.help or ""))
            if option.name == "mode":
                print("")
                print("""%-34s accept - accept all email with code 250, 251,"""
                      """ 252 or 253""" % "")
                print("""%-34s bounce - bounce all email with a random code,"""
                      """\n%-37sexcluding 250, 251, 252, 253""" % ("", ""))
                print("""%-34s random - randomly accept or bounce all email"""
                      """ with a random code""" % "")
                print("""%-34s unavailable - server always respondes with"""
                      """ code 421\n%-37s- service is unavailable""" %
                      ("", ""))
                print("""%-34s offline - server always responds with code"""
                      """ 521 - server\n%-37sdoes not accept mail""" %
                      ("", ""))
    print("")
