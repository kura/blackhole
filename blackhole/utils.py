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
blackhole.utils - A utility module used for
methods and features that do not belong in
their own module.
"""

import os
import sys
import grp
import pwd
import random
import signal
import socket

import setproctitle
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
        for pid in frame.f_locals['children'].keys():
            os.kill(pid, signal.SIGTERM)
    except KeyError:
        # not the parent
        pass
    if os.path.exists(options.pid):
        os.remove(options.pid)
    sys.exit(0)


def set_process_title():
    """
    Set the title of the process.

    If the process is the master, set
    a master title, otherwise set
    worker.
    """
    if os.path.exists(options.pid):
        pid = int(open(options.pid, 'r').read().strip())
        if pid == os.getpid():
            setproctitle.setproctitle("blackhole: master")
        else:
            setproctitle.setproctitle("blackhole: worker")


def email_id():
    """
    Generate an HEX ID to assign to each
    connection.

    Will be reused later down the line
    due to the limited number of characters.
    """
    alpha = list("1234567890ABCDEF")
    return ''.join(random.choice(alpha) for x in range(10))


def get_mailname():
    """
    Return a mailname for HELO.

    Reads /etc/mailname if present
    and falls back to socket.getfqdn
    """
    mailname_file = "/etc/mailname"
    if os.path.exists(mailname_file):
        mnc = open(mailname_file, 'r').read().strip()
        if mnc != "":
            return mnc
    return socket.getfqdn()
