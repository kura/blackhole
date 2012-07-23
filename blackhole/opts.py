from tornado.options import define


define('host', default="0.0.0.0", metavar="IP", type=str,
       help="IP address to bind go [default: 0.0.0.0]",
       group="Blackhole")
define('port', default=25, metavar="PORT", type=int,
       help="Port to listen for connections on [default:  25]",
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
define("log", default="/tmp/blackhole.io",
	   metavar="FILE", help="File to write logs to (not very verbose) [default: /tmp/blackhole.log]",
	   group="Blackhole")
