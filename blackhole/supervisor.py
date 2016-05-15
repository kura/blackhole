# (The MIT License)
#
# Copyright (c) 2016 Kura
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

"""Provides functionality to create the supervisor process."""


import asyncio
import logging
import signal
import os

from .config import Config
from .control import server
from .exceptions import BlackholeRuntimeException
from .worker import Worker


__all__ = ('Supervisor', )


logger = logging.getLogger('blackhole.supervisor')


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]


class Supervisor(metaclass=Singleton):
    """
    The supervisor process.

    Responsible for monitoring and controlling child processes via an
    internal map of workers and the children they manage.
    """

    def __init__(self, loop=None):
        """
        Initialise the supervisor.

        Loads the configuration and event loop.

        :param loop: The event loop to use.
        :type loop: :any:`syncio.unix_events._UnixSelectorEventLoop` or
                    :any:`None` to get the current event loop using
                    :any:`asyncio.get_event_loop`.
        :raises: :any:`blackhole.exceptions.BlackholeRuntimeException`
        """
        logger.debug('Initiating the supervisor')
        self.config = Config()
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        self.socks = []
        self.workers = []
        try:
            self.generate_servers()
        except BlackholeRuntimeException:
            self.close_socks()
            raise BlackholeRuntimeException()

    def generate_servers(self):
        """Spawn all of the required sockets and TLS contexts."""
        logger.debug('Attaching sockets to the supervisor')
        for host, port, family, flags in self.config.listen:
            aserver = server(host, port, family, flags)
            self.socks.append(aserver)
            logger.debug('Attaching %s:%s with flags %s', host, port, flags)

        tls_conf = (self.config.tls_cert, self.config.tls_key)
        if len(self.config.tls_listen) > 0 and all(tls_conf):
            for host, port, family, flags in self.config.tls_listen:
                aserver = server(host, port, family, flags, use_tls=True)
                self.socks.append(aserver)
                logger.debug('Attaching %s:%s (TLS) with flags %s',
                             host, port, flags)

    def run(self):
        """
        Start all workers and their children, attach signals and run the event
        loop 'forever'.
        """
        self.start_workers()
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
        self.loop.run_forever()

    def start_workers(self):
        """Start each worker and it's child process."""
        logger.debug('Starting workers')
        for idx in range(self.config.workers):
            num = '{}'.format(idx + 1)
            logger.debug('Creating worker: %s', num)
            self.workers.append(Worker(num, self.socks, self.loop))

    def stop_workers(self):
        """Stop the workers and their respective child process."""
        logger.debug('Stopping workers')
        worker_num = 1
        for worker in self.workers:
            logger.debug('Stopping worker: %s', worker_num)
            worker.stop()
            worker_num += 1

    def close_socks(self):
        """Close all opened sockets."""
        for sock in self.socks:
            sock['sock'].close()

    def stop(self, signum=None, frame=None):
        """
        Terminate all of the workers.

        Generally should be called by a signal, nothing else.

        :param signum: A signal number.
        :type signum: :any:`int`
        :param frame: Interrupted stack frame.
        :type frame: :any:`frame`
        :raises: :any:`SystemExit` -- :any:`os.EX_OK`
        """
        self.loop.stop()
        self.stop_workers()
        self.close_socks()
        logger.debug('Stopping supervisor')
        try:
            self.loop.stop()
        except RuntimeError:
            pass
        raise SystemExit(os.EX_OK)
