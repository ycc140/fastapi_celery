# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-07-15 16:23:58
     $Rev: 22
"""

# BUILTIN modules
import sys
import logging
from typing import cast
from types import FrameType

# Third party modules
from loguru import logger

# local modules
from ..config.setup import config


# ---------------------------------------------------------
#
class InterceptHandler(logging.Handler):
    """ Send logs to loguru logging from Python logging module. """

    def emit(self, record: logging.LogRecord):
        """  Move the specified logging record to loguru.

        :param record: Original python log record.
        """
        try:
            level = logger.level(record.levelname).name

        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2

        while frame.f_code.co_filename == logging.__file__:
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(
            depth=depth,
            exception=record.exc_info).log(
            level,
            record.getMessage()
        )


# ---------------------------------------------------------
#
def create_unified_logger() -> logger:
    """ Return unified Loguru logger object.

    :return: unified Loguru logger object.
    """

    level = config.log_level

    # Remove all existing loggers.
    logger.remove()

    # Create a basic Loguru logging config.
    logger.add(
        enqueue=False,
        colorize=True,
        backtrace=True,
        sink=sys.stderr,
        level=level.upper(),
        format=config.log_format,
        diagnose=config.log_diagnose,
    )

    # Prepare to incorporate python standard logging.
    seen = set()
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    for logger_name in logging.root.manager.loggerDict.keys():

        if logger_name not in seen:
            seen.add(logger_name)
            mod_logger = logging.getLogger(logger_name)
            mod_logger.handlers = [InterceptHandler()]
            mod_logger.propagate = False

    return logger.bind(request_id=None, method=None)
