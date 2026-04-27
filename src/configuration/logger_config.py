import atexit
import json
import logging
import logging.config
import os

def safe_load_config() -> logging.Logger | None:
    environment = os.environ.get("ENVIRONMENT")

    try:
        config_file = f'/app/logs/logging_config_{environment}.json'
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

def setup_logging(name) -> logging.Logger:
    """
    Set up logging configuration.
    """
    logger = safe_load_config()
    logger.info(f"Logging is set up in: {name}")

    return logger
