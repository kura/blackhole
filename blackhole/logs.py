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
    logger_handlers = log_config['loggers']['blackhole']['handlers']
    if args.debug and not args.test:
        log_config['loggers']['blackhole']['level'] = logging.DEBUG
        log_config['handlers']['debug_handler'] = debug_handler
        logger_handlers.append('debug_handler')
    else:
        log_config['handlers']['default_handler'] = default_handler
        logger_handlers.append('default_handler')
    dictConfig(log_config)
