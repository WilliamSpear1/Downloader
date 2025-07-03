import logging
import logging.config
from pathlib import Path

#Ensure the logs directory exists
Path("logs").mkdir(parents=True, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console_handler": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": logging.INFO,
        },
    },
    "loggers": {
        "app_logger": {
            "handlers": ["console_handler"],
            "level": logging.INFO,
            "propagate": False,
        }
    }
}

def setup_logging():
    """
    Set up logging configuration.
    """
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger('app_logger')
    logger.info("Logging is set up.")
    return logger