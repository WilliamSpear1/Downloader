import datetime
import gzip
import logging
import logging.config
import os
import shutil
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from gunicorn.glogging import Logger

#Ensure the logs directory exists
Path("logs").mkdir(parents=True, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            'format': '[%(asctime)s] [%(levelname)s] [PID:%(process)d] [TID:%(thread)d] %(name)s: %(message)s',
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console_handler": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": logging.INFO
        },
        "file_handler": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "default",
            "filename": "downloader.logs",
            "when": "midnight",
            "atTime": datetime.time(2, 0, 0),
            "backupCount": 3,
            "level": logging.INFO
        },
    },
    "loggers": {
        "app_logger": {
            "handlers": ["console_handler", "file_handler"],
            "level": logging.INFO,
            "propagate": False,
        }
    }
}

# Compressor
"""
:param source -> path to rotated log file.
:para dest -> destination filename without the .gz extension

Adds the gz extension to file
"""
def compress_rotated_log(source, dest) -> None:
    #rb -> read binary mode
    #wb -> write binary mode
    #f_in -> file object that is being read from

    with open(source, 'rb') as f_in, gzip.open(dest + '.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    os.remove(source)

def add_rotator(logger) -> None:
    for handler in logger.handlers:
        if isinstance(handler, TimedRotatingFileHandler):
            handler.rotator = compress_rotated_log
            handler.namer = lambda name: name + '.gz'

def setup_logging(name) -> Logger:
    """
    Set up logging configuration.
    """
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger('app_logger')
    add_rotator(logger)
    logger.info("Logging is set up in: %s", name)
    return logger