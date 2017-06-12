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
