import sys
import os
import time
import atexit
from signal import SIGTERM


class Daemon:

    def __init__(self, pidfile, stdin="/dev/null",
                 stdout="/dev/null", stderr="/dev/null"):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            print "fork #1 failed: %d (%s)\n" % (e.errno, e.strerror)
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            print "fork #2 failed: %d (%s)\n" % (e.errno, e.strerror)
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        try:
            pid = int(file(self.pidfile, 'r').read().strip())
        except IOError:
            pid = None
        if pid:
            if os.path.exists("/proc/%s" % pid):
                message = "pidfile %s already exist. Daemon already running?\n"
                print message % self.pidfile
                sys.exit(1)
            else:
                print "Stale pid %s. Removing" % pid
                self.delpid()

        self.daemonize()

    def stop(self):
        """
        Stop the daemon
        """
        try:
            pid = int(file(self.pidfile, 'r').read().strip())
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            print message % self.pidfile
            return

        try:
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print err
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def status(self):
        if not os.path.exists(self.pidfile):
            print "not running"
            sys.exit()
        pid = open(self.pidfile, "r").read()[:-1]
        stats = os.path.join("/proc", pid, "status")
        if os.path.exists(stats):
            c = open(stats, "r").read().split("\n")
            _, state = c[1].split("\t")
            if not state.startswith("Z"):
                print "running"
            else:
                print "zombie"
        else:
            print "not running"
