import logging

from blackhole.logs import configure_logs


class Args(object):
    def __init__(self, args):
        for arg in args:
            setattr(self, arg[0], arg[1])


def test_default():
    args = Args((('debug', False), ('test', False)))
    logger = logging.getLogger('blackhole')
    configure_logs(args)
    assert logger.handlers[0].level is logging.INFO


def test_debug_no_test():
    args = Args((('debug', True), ('test', False)))
    logger = logging.getLogger('blackhole')
    configure_logs(args)
    assert logger.handlers[0].level is logging.DEBUG


def test_debug_and_test():
    args = Args((('debug', True), ('test', True)))
    logger = logging.getLogger('blackhole')
    configure_logs(args)
    assert logger.handlers[0].level is logging.INFO


def test__test():
    args = Args((('debug', False), ('test', True)))
    logger = logging.getLogger('blackhole')
    configure_logs(args)
    assert logger.handlers[0].level is logging.INFO
