import sys
import os
import atexit

from blackhole.exceptions import DaemonException


class Daemon(object):

    def __init__(self, pidfile):
        self.pidfile = pidfile

    def daemonize(self):
        self.fork()
        os.chdir(os.path.sep)
        os.setsid()
        os.umask(0)
        self.fork()
        atexit.register(self.delpid)
        self.pid = os.getpid()

    def fork(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            raise DaemonException(err.strerror)

    def delpid(self):
        os.remove(self.pidfile)

    @property
    def pid(self):
        if os.path.exists(self.pidfile):
            try:
                pid = open(self.pidfile, 'r').read().strip()
            except IOError as err:
                raise(err.strerror)
            if not os.path.exists(os.path.join(os.path.sep, 'proc', pid)):
                self.delpid()
            return int(pid)
        return None

    @pid.setter
    def pid(self, pid):
        pid = str(pid)
        try:
            with open(self.pidfile, 'w+') as pidfile:
                pidfile.write("{}\n".format(pid))
        except (IOError, FileNotFoundError) as err:
            raise DaemonException(err.strerror)

    @pid.deleter
    def pid(self):
        self.delpid()
