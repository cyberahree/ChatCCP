from discord.utils import _ColourFormatter

import logging

def setup_logging() -> None:
    formatter = _ColourFormatter()

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)