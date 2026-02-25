import datetime
import gzip
import json
import logging
import logging.config
import os
import shutil
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

#Ensure the logs directory exists
Path("/var/log/downloader").mkdir(parents=True, exist_ok=True)
environment = os.environ.get("ENVIRONMENT")

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

    with open(source, 'rb') as f_in, gzip.open(dest, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

    if os.path.exists(source):
        os.remove(source)

def add_rotator(logger) -> None:
    for handler in logger.handlers:
        if isinstance(handler, TimedRotatingFileHandler):
            handler.rotator = compress_rotated_log
            handler.namer = lambda name: name + '.gz'

def safe_load_config() -> logging.Logger | None:
    try:
        config_file = f'/app/logs/logging_config_{environment}.json'
        with open(config_file, 'r') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
        return logging.getLogger()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.basicConfig(level=logging.DEBUG)
        logging.warning("Config file not found, using basicConfig with DEBUG level.")
        return logging.getLogger()

def setup_logging(name) -> logging.Logger:
    """
    Set up logging configuration.
    """
    logger = safe_load_config()
    add_rotator(logger)
    logger.info(f"Logging is set up in: {name}")

    return logger
