"""blackhole.utils - A utility module used for
methods and features that do not belong in
their own module."""

import os
import sys
import grp
import pwd
import signal

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


def terminate(signum, frame):
    """
    Terminate the parent process and send signals
    to shut down it's children

    Iterates over the child pids in the frame
    and sends the SIGTERM signal to shut them
    down.
    """
    try:
        for pid in frame.f_locals['children'].iterkeys():
            os.kill(pid, signal.SIGTERM)
    except KeyError:
        # not the parent
        pass
    if os.path.exists(options.pid):
        os.remove(options.pid)
    sys.exit(0)
