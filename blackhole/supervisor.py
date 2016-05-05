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

"""
blackhole.supervisor.

This module houses functionality to create the supervisor process.
"""


import asyncio
import logging
import os
import signal

from blackhole.config import Config
from blackhole.control import _server
from blackhole.worker import Worker


logger = logging.getLogger('blackhole.supervisor')


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]


class Supervisor(metaclass=Singleton):
    """A supervisor process."""

    def __init__(self, loop=None):
        """
        Initialise the supervisor.

        Loads the configuration and event loop.
        """
        self.config = Config()
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        self.workers = []
        logger.debug('Spawning supervisor process')

    def spawn(self):
        """
        Spawn all of the required sockets and TLS context.

        :returns: :any:`list` -- a list of sockets and TLS context.
        """
        socks = []
        logger.debug('Starting workers')
        for host, port, family in self.config.listen:
            socks.append(_server(host, port, family))
        tls_conf = (self.config.tls_cert, self.config.tls_key)
        if len(self.config.tls_listen) > 0 and all(tls_conf):
            for host, port, family in self.config.tls_listen:
                socks.append(_server(host, port, family, use_tls=True))
        return socks

    def create(self):
        """Create the worker processes."""
        socks = self.spawn()
        for idx in range(self.config.workers):
            logger.debug('Creating worker: %s', idx + 1)
            self.workers.append(Worker(socks, self.loop))
        self.loop.add_signal_handler(signal.SIGINT, lambda: self.loop.stop())

    def run(self):
        """Run event loop forever."""
        self.loop.run_forever()

    def stop(self, signum=None, frame=None):
        """Terminate all of the workers."""
        logger.debug('Stopping workers')
        worker_num = 1
        for worker in self.workers:
            logger.debug('Stopping worker: %s', worker_num)
            worker.kill()
            worker_num += 1
        raise SystemExit(os.EX_OK)
