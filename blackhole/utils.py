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
blackhole.utils.

Provides utility functions to blackhole.
"""


import os
import random
import socket
import time


def mailname():
    """
    A fully qualified domain name for HELO and EHLO.

    .. note::

       Prefers content of /etc/mailname, falls back on `socket.getfqdn`.

    :returns: str -- fully qualified domain name.
    """
    mailname_file = '/etc/mailname'
    if os.path.exists(mailname_file):
        mailname_content = open(mailname_file, 'r').read().strip()
        if mailname_content != '':
            return mailname_content
    return socket.getfqdn()


def message_id():
    """
    A globally unique random string in RFC 2822 Message-ID format.

    .. note::

       Message-ID is comprised of datetime.PID.random_int.id@f.q.dn.

    :returns: str -- RFC 2822 Message-ID.
    """
    def id_generator():
        i = 0
        while True:
            yield i
            i += 1
    datetime = time.strftime('%Y%m%d%H%M%S', time.gmtime())
    pid = os.getpid()
    rand = random.randrange(2**31-1)
    id_gen = id_generator()
    return '<{}.{}.{}.{}@{}>'.format(datetime, pid, rand, next(id_gen),
                                     mailname())
