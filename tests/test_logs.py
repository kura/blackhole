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

import logging

import pytest

from blackhole.logs import configure_logs

from ._utils import (Args, cleandir, create_config, create_file, reset)


@pytest.mark.usefixtures('reset', 'cleandir')
def test_default():
    args = Args((('debug', False), ('test', False), ('quiet', False)))
    logger = logging.getLogger('blackhole')
    configure_logs(args)
    assert logger.handlers[0].level is logging.INFO


@pytest.mark.usefixtures('reset', 'cleandir')
def test_debug():
    args = Args((('debug', True), ('test', False), ('quiet', False)))
    logger = logging.getLogger('blackhole')
    configure_logs(args)
    assert logger.handlers[0].level is logging.DEBUG


@pytest.mark.usefixtures('reset', 'cleandir')
def test_test():
    args = Args((('debug', False), ('test', True), ('quiet', False)))
    logger = logging.getLogger('blackhole')
    configure_logs(args)
    assert logger.handlers[0].level is logging.INFO


@pytest.mark.usefixtures('reset', 'cleandir')
def test_quiet():
    args = Args((('debug', False), ('test', False), ('quiet', True)))
    logger = logging.getLogger('blackhole')
    configure_logs(args)
    assert logger.handlers[0].level is logging.ERROR
