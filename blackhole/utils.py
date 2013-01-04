import os
import sys
import grp
import pwd

from tornado.options import options

from blackhole.log import log


def setgid():
    """
    Change our existing group.

    Used to drop from root privileges down to a less
    privileged group.

    MUST be called BEFORE setuid, not after.
    """
    try:
        os.setgid(grp.getgrnam(options.group).gr_gid)
    except KeyError:
        log.error("Group '%s' does not exist" % options.group)
        sys.exit(1)
    except OSError:
        log.error("You do not have permission to switch to group '%s'"
                  % options.group)
        sys.exit(1)


def setuid():
    """
    Change our existing user.

    Used to drop from root privileges down to a less
    privileged user

    MUST be called AFTER setgid, not before.
    """
    try:
        os.setuid(pwd.getpwnam(options.user).pw_uid)
    except KeyError:
        log.error("User '%s' does not exist" % options.user)
        sys.exit(1)
    except OSError:
        log.error("You do not have permission to switch to user '%s'"
                  % options.user)
        sys.exit(1)
