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
blackhole.child.

This module houses the functionality to spawn child processes.
"""


import asyncio
import logging
import os
import signal

from blackhole.smtp import Smtp


logger = logging.getLogger('blackhole.child')


class Child:
    """A child process."""

    def __init__(self, up_read, down_write, socks):
        """
        Initialise a child process.

        :param up_read:
        :type up_read: :any:`os.pipe`
        :param down_write:
        :type down_write: :any:`os.pipe`
        :param socks: a list of sockets
        :type socks: :any:`list`
        """
        self.up_read = up_read
        self.down_write = down_write
        self.socks = socks

    def start(self):
        """Start the child process."""
        self.loop = loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        def stop():
            """Stop the child process."""
            self.loop.stop()
            os._exit(0)
        loop.add_signal_handler(signal.SIGINT, stop)

        for sock in self.socks:
            ctx = sock['ctx'] if 'ctx' in sock else None
            sock = sock['sock']
            f = loop.create_server(lambda: Smtp(), sock=sock, ssl=ctx)
            loop.run_until_complete(f)
        asyncio.get_event_loop().run_forever()
        os._exit(0)
