import logging

from blackhole.logs import configure_logs


class Args(object):
    def __init__(self, args):
        for arg in args:
            setattr(self, arg[0], arg[1])


def test_default():
    args = Args((('debug', False), ('test', False), ('quiet', False)))
    logger = logging.getLogger('blackhole')
    configure_logs(args)
    assert logger.handlers[0].level is logging.INFO


def test_debug():
    args = Args((('debug', True), ('test', False), ('quiet', False)))
    logger = logging.getLogger('blackhole')
    configure_logs(args)
    assert logger.handlers[0].level is logging.DEBUG


def test_test():
    args = Args((('debug', False), ('test', True), ('quiet', False)))
    logger = logging.getLogger('blackhole')
    configure_logs(args)
    assert logger.handlers[0].level is logging.INFO


def test_quiet():
    args = Args((('debug', False), ('test', False), ('quiet', True)))
    logger = logging.getLogger('blackhole')
    configure_logs(args)
    assert logger.handlers[0].level is logging.ERROR
