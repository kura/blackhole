"""blackhole.log - Logging configuration for the blackhole
server."""

import logging

from tornado.options import options


logging.basicConfig(format="%(message)s")
log = logging.getLogger(__name__)
file_handler = logging.FileHandler(options.log)
log_level = logging.INFO
if options.debug:
	log_level = logging.DEBUG
log.setLevel(log_level)
file_handler.setLevel(log_level)
file_formatter = logging.Formatter("%(asctime)s - %(message)s")
file_handler.setFormatter(file_formatter)
log.addHandler(file_handler)