import sys
from tornado.options import define, options
from blackhole import __pname__


define('host', default="0.0.0.0", metavar="IP", type=str,
       help="IP address to bind go [default: 0.0.0.0]",
       group="Blackhole")
define('port', default=25, metavar="PORT", type=int,
       help="Port to listen for connections on [default: 25]",
       group="Blackhole")
define('pid', default="/tmp/blackhole.pid", metavar="FILE", type=str,
       help="File to write process information to [default: /tmp/blackhole.pid]",
       group="Blackhole")
define("conf", metavar="FILE",
       help="Config file to parse and use. Overrides command line args",
       group="Blackhole")
define("user", default="blackhole",
       metavar="USER", help="User to drop privs to during run time. [default: blackhole]",
       group="Blackhole")
define("group", default="blackhole",
       metavar="GROUP", help="Group to drop privs to during run time. [default: blackhole]",
       group="Blackhole")
define("log", default="/tmp/blackhole.log",
       metavar="FILE", help="File to write logs to (not very verbose) [default: /tmp/blackhole.log]",
       group="Blackhole")
define("mode", default="accept",
       metavar="MODE", help="Mode to run blackhole in (accept, bounce, random, unavailable, offline) [default: accept]",
       group="Mode")


def print_help(file=sys.stdout):
    """Prints all the command line options to stdout."""
    print "Usage: %s [OPTIONS] (start|stop|status)" % (__pname__)
    print >> file, "\nOptions:"
    by_group = {}
    opts = {}
    for option, value in options.iteritems():
        # hack to bypass Tornado options
        if option.startswith(("host", "port", "pid", "conf",
                              "user", "group", "mode")):
            opts[option] = value
    for option in opts.itervalues():
        by_group.setdefault(option.group_name, []).append(option)

    for filename, o in sorted(by_group.items()):
        # if filename:
        #     print >> file, filename
        o.sort(key=lambda option: option.name)
        for option in o:
            prefix = option.name
            if option.metavar:
                prefix += "=" + option.metavar
            print >> file, "  --%-30s %s" % (prefix, option.help or "")
            if option.name == "mode":
                print >> file, "%-34s accept - accept all email with code 250, 251, 252 or 253" % ""
                print >> file, "%-34s bounce - bounce all email with a random code, excluding 250, 251, 252, 253" % ""
                print >> file, "%-34s random - randomly accept or bounce all email with a random code" % ""
                print >> file, "%-34s unavailable - server always respondes with code 421 - service is unavailable" % ""
                print >> file, "%-34s offline - server always responds with code 521 - server does not accept mail" % ""
    print >> file
