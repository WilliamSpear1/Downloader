import atexit
import json
import logging
import logging.config
import os

"""
Load the logging configuration from the environment-specific JSON config file.

Reads the ENVIRONMENT variable to determine which config file to load
(e.g., logging_config_prod.json or logging_config_dev.json). Falls back
to basic DEBUG logging if the config file is missing or invalid.

Returns:
    The root logger instance configured with the loaded settings.
"""
def safe_load_config() -> logging.Logger | None:
    environment = os.environ.get("ENVIRONMENT")

    try:
        config_file = f'/app/src/configuration/logging_config_{environment}.json'
        with open(config_file, 'r') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
        queue_handler = logging.getHandlerByName("queue_handler")
        if queue_handler:
            queue_handler.listener.start()
            atexit.register(queue_handler.listener.stop)
        # console_handler = logging.getHandlerByName("console_handler")
        # file_handler = logging.handlers.RotatingFileHandler("file_handler")
        #
        # listener = logging.handlers.QueueListener(log_queue, console_handler, file_handler, respect_handler_level=True)
        #
        # logging.config.dictConfig(config)

        return logging.getLogger()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.basicConfig(level=logging.DEBUG)
        logging.warning("Config file not found, using basicConfig with DEBUG level.")
        return logging.getLogger()

"""
Set up and return a logger for the given module.

Loads the logging configuration and logs an info message indicating
which module has been configured.

Args:
    name: The module name (typically __name__) used to identify the logger source.

Returns:
    A configured logger instance.
"""
def setup_logging(name: str) -> logging.Logger:
    logger = safe_load_config()
    logger.info(f"Logging is set up in: {name}")

    return logger
