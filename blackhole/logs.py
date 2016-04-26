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


DEBUG_FORMAT = ('[%(asctime)s] [%(levelname)s] blackhole.%(module)s:'
                '%(message)s')

LOG_CONFIG = {
    'version': 1,
    'formatters': {
        'console': {'format': '%(message)s'},
        'debug': {'format': DEBUG_FORMAT},
    },
    'handlers': {
    },
    'loggers': {
        'blackhole': {'handlers': [], 'level': logging.INFO},
    }
}

DEBUG_HANDLER = {'class': 'logging.StreamHandler',
                 'formatter': 'debug',
                 'level': logging.DEBUG}

DEFAULT_HANDLER = {'class': 'logging.StreamHandler',
                   'formatter': 'console',
                   'level': logging.INFO}


def configure_logs(args):
    """
    Configure the logging module.

    :param args:
    :type args: Parameters parsed from :any:`argparse`.
    """
    logger_handlers = LOG_CONFIG['loggers']['blackhole']['handlers']
    if args.debug and not args.test:
        LOG_CONFIG['loggers']['blackhole']['level'] = logging.DEBUG
        LOG_CONFIG['handlers']['default_handler'] = DEBUG_HANDLER
        logger_handlers.append('default_handler')
    else:
        LOG_CONFIG['loggers']['blackhole']['level'] = logging.INFO
        LOG_CONFIG['handlers']['default_handler'] = DEFAULT_HANDLER
        logger_handlers.append('default_handler')
    dictConfig(LOG_CONFIG)
