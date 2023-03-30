""" Logger for wenet project

use syslog

Copyright (c) 2023 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,


"""
import logging
import logging.handlers
from os import environ

from dotenv import load_dotenv

load_dotenv()


def create_logger(name: str = "wenet-undefined"):
    """create a logger with the correct configuration"""

    logger = logging.getLogger(name)
    logger_level = int(environ.get("LOGGER_LEVEL", "20"))
    logger_format = environ.get(
        "LOGGER_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger_file = environ.get("LOGGER_FILE", "activities.log")
    logger.setLevel(logger_level)
    formatter = logging.Formatter(logger_format)

    log_file = logging.handlers.WatchedFileHandler(logger_file)
    ch = logging.StreamHandler()

    log_file.formatter = formatter
    ch.formatter = formatter

    logger.addHandler(log_file)
    logger.addHandler(ch)
    return logger
