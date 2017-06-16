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

# pylama:skip=1

import asyncio
import logging
import os
import pathlib
import tempfile

import pytest

from blackhole.utils import Singleton

logging.getLogger('blackhole').addHandler(logging.NullHandler())


@pytest.fixture()
def cleandir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)


@pytest.fixture()
def reset():
    Singleton._instances = {}


def create_config(data):
    cwd = os.getcwd()
    path = os.path.join(pathlib.Path(cwd),
                        pathlib.Path('test.conf'))
    with open(path, 'w') as cfile:
        cfile.write('\n'.join(data))
    return path


def create_file(name, data=''):
    cwd = os.getcwd()
    path = os.path.join(pathlib.Path(cwd), pathlib.Path(name))
    with open(path, 'w') as ffile:
        ffile.write(str(data))
    return path


class Args(object):
    def __init__(self, args=None):
        if args is not None:
            for arg in args:
                setattr(self, arg[0], arg[1])
