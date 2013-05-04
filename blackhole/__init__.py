"""Blackhole is an email MTA that pipes all mail to /dev/null

Blackhole is just any other MTA out there except it does not
actual do any disk I/O with the mail it receives. It is simply
accept or rejected based on configuration and pretends it's
actually done something."""

__author__ = "Kura"
__copyright__ = "None"
__credits__ = ["Kura", ]
__license__ = "MIT"
__version__ = "1.6.0"
__maintainer__ = "Kura"
__email__ = "kura@kura.io"
__status__ = "Stable"

__pname__ = "blackhole"
__desc__ = "blackhole.io MTA"

__fullname__ = "%s %s (%s)" % (__pname__, __version__, __status__)
