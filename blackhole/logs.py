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
blackhole.logs.

Configure logging for blackhole.
"""


import logging
from logging.config import dictConfig


debug_format = '[%(levelname)s] blackhole.%(module)s: %(message)s'
log_config = {
    'version': 1,
    'formatters': {
        'console': {'format': '%(message)s'},
        'debug': {'format': debug_format}
    },
    'handlers': {
    },
    'loggers': {
        'blackhole': {'handlers': [], 'level': logging.INFO},
    }
}

debug_handler = {'class': 'logging.StreamHandler',
                 'formatter': 'debug', 'level': logging.DEBUG}
default_handler = {'class': 'logging.StreamHandler',
                   'formatter': 'console', 'level': logging.INFO}


def configure_logs(args):
    """
    Configure the logging module.

    :param args:
    :type args: Parameters parsed from `argparse`.
    """
    logger_handlers = log_config['loggers']['blackhole']['handlers']
    if args.debug and not args.test:
        log_config['loggers']['blackhole']['level'] = logging.DEBUG
        log_config['handlers']['debug_handler'] = debug_handler
        logger_handlers.append('debug_handler')
    else:
        log_config['handlers']['default_handler'] = default_handler
        logger_handlers.append('default_handler')
    dictConfig(log_config)
