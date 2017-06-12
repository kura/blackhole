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
