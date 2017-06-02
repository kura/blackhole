# (The MIT License)
#
# Copyright (c) 2013-2017 Kura
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

"""Provides daemonisation functionality."""


import atexit
import os

from .exceptions import DaemonException


__all__ = ('Daemon', )
"""Tuple all the things."""


class Singleton(type):
    """A singleton for :class:`blackhole.daemon.Daemon`."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Singleton for :class:`blackhole.daemon.Daemon`.

        :param cls:
        :type cls: :class:`blackhole.daemon.Daemon`
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]


class Daemon(metaclass=Singleton):
    """An object for handling daemonisation."""

    def __init__(self, pidfile):
        """
        Create an instance of :class:`blackhole.daemon.Daemon`.

        :param pidfile: A path to store the pid
        :type pidfile: :py:obj:`str`

        .. note::

           Registers an :py.func:`atexit.register` signal to delete the pid on
           exit.
        """
        self.pidfile = pidfile
        self.pid = os.getpid()
        atexit.register(self._exit)

    def daemonize(self):
        """Daemonize the process."""
        self.fork()
        os.chdir(os.path.sep)
        os.setsid()
        os.umask(0)
        self.pid = os.getpid()

    def _exit(self, signum=None, frame=None):
        """
        Call on exit using :py:func:`atexit.register` or via a signal.

        :param signum: The signal number.
        :type: signum: :py:obj:`int`
        :param frame: The stack frame when interrupted.
        :type frame: :py:obj:`frame`
        """
        del self.pid

    def fork(self):
        """
        Fork off the process.

        :raises: :py:func:`os._exit` -- :py:obj:`os.EX_OK`
        :raises: :class:`blackhole.exceptions.DaemonException`
        """
        try:
            pid = os.fork()
            if pid > 0:
                os._exit(os.EX_OK)
        except OSError as err:
            raise DaemonException(err.strerror)

    @property
    def pid(self):
        """
        Pid of the process, if it's been daemonised.

        :raises: :exc:`blackhole.exceptions.DaemonException` if pid cannot be
                 read from the filesystem.
        :returns: The current pid.
        :rtype: :py:obj:`int` or :py:obj:`None`

        .. note::

           The pid is retrieved from the filestem.
           If the pid does not exist in /proc, the pid is deleted.
        """
        if os.path.exists(self.pidfile):
            try:
                pid = open(self.pidfile, 'r').read().strip()
                if pid != '':
                    return int(pid)
            except (FileNotFoundError, IOError, PermissionError,
                    OSError) as err:
                raise DaemonException(err.strerror)
        return None

    @pid.setter
    def pid(self, pid):
        """
        Write the pid to the filesystem.

        :raises: :exc:`daemon.daemon.DaemonException` if writing to filesystem
                 fails.
        :param pid: the process's pid.
        :type pid: :py:obj:`int`
        """
        pid = str(pid)
        try:
            with open(self.pidfile, 'w+') as pidfile:
                pidfile.write("{0}\n".format(pid))
        except (IOError, FileNotFoundError, PermissionError) as err:
            raise DaemonException(err.strerror)

    @pid.deleter
    def pid(self):
        """Delete the pid from the filesystem."""
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)
