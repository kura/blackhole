import logging

from tornado.options import options


logging.basicConfig(format="%(message)s")
log = logging.getLogger(__name__)
file_handler = logging.FileHandler(options.log)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s - %(message)s")
file_handler.setFormatter(file_formatter)
log.addHandler(file_handler)
