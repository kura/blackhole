import logging
import os
import tempfile

import pytest

from blackhole.config import Singleton as CSingleton
from blackhole.daemon import Singleton as DSingleton
from blackhole.supervisor import Singleton as SSingleton


logging.getLogger('blackhole').addHandler(logging.NullHandler())


@pytest.fixture()
def cleandir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)


@pytest.fixture()
def reset_conf():
    CSingleton._instances = {}


@pytest.fixture()
def reset_daemon():
    DSingleton._instances = {}


@pytest.fixture()
def reset_supervisor():
    SSingleton._instances = {}


def create_config(data):
    cwd = os.getcwd()
    path = os.path.join(cwd, 'test.conf')
    with open(path, 'w') as cfile:
        cfile.write('\n'.join(data))
    return path


def create_file(name, data=''):
    cwd = os.getcwd()
    path = os.path.join(cwd, name)
    with open(path, 'w') as ffile:
        ffile.write(str(data))
    return path


class Args(object):
    def __init__(self, args=None):
        if args is not None:
            for arg in args:
                setattr(self, arg[0], arg[1])
