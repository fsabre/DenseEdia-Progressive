import logging

logger = logging.getLogger("denseedia")
logger.setLevel(logging.WARNING)

stream_h = logging.StreamHandler()
stream_h.setFormatter(logging.Formatter("%(levelname)s\t%(message)s"))
logger.addHandler(stream_h)
