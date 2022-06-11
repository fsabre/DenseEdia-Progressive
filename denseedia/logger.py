"""Define the main logger."""

import logging

formatter = logging.Formatter("%(asctime)s::%(levelname)s::%(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger = logging.getLogger("denseedia")
logger.setLevel(logging.WARNING)
logger.addHandler(stream_handler)


class NoNewlineStreamHandler(logging.StreamHandler):
    """Replace the newlines by spaces. Made to fix PonyORM logger."""

    def emit(self, record):
        record.msg = record.msg.replace("\n", " ")
        super().emit(record)


pony_logger = logging.getLogger("pony.orm")
pony_logger.setLevel(logging.DEBUG)
no_newline_steam_handler = NoNewlineStreamHandler()
no_newline_steam_handler.setFormatter(formatter)
pony_logger.addHandler(no_newline_steam_handler)
