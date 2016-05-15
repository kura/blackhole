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

"""Provides utility functionality."""

import os
import random
import re
import socket
import time


__all__ = ('mailname', 'message_id', 'get_version')


def mailname(mailname_file='/etc/mailname'):
    """
    A fully qualified domain name for HELO and EHLO.

    :param mailname_file: A path to the mailname file.
    :type mailname_file: :any:`str`
    :returns: A domain name.
    :rtype: :any:`str`

    .. note::

       Prefers content of `mailname_file`, falls back on :any:`socket.getfqdn`
       if `mailname_file` does not exist or cannot be opened for reading.
    """
    if os.access(mailname_file, os.R_OK):
        mailname_content = open(mailname_file, 'r').readlines()
        if len(mailname_content) == 0:
            return socket.getfqdn()
        mailname_content = mailname_content[0].strip()
        if mailname_content != '':
            return mailname_content
    return socket.getfqdn()


def message_id(domain):
    """
    Return a string suitable for RFC 2822 compliant Message-ID.

    :param domain: A fully qualified domain.
    :type domain :any:`str`
    :returns: An RFC 2822 compliant Message-ID.
    :rtype: :any:`str`
    """
    timeval = int(time.time() * 100)
    pid = os.getpid()
    randint = random.getrandbits(64)
    return '<{}.{}.{}@{}>'.format(timeval, pid, randint, domain)


def get_version():
    """
    Extract the __version__ from a file without importing it.

    :return: The version that was extracted.
    :rtype: :any:`str`
    :raises: :any:`AssertionError`
    """
    path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(path, '__init__.py')
    pattern = re.compile(r'(?P<version>\d+\.\d+(?:\.\d+)?(?:(?:a|b|rc)\d+)?)')
    if not os.access(filepath, os.R_OK):
        raise AssertionError('No __init__.py file found')
    with open(filepath) as fp:
        for line in fp:
            if line.startswith('__version__'):
                mo = pattern.search(line)
                assert mo, 'No valid __version__ string found'
                return mo.group('version')
    raise AssertionError('No __version__ assignment found')
