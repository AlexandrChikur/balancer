import logging.config

LOGGER_NAME = __name__

logger_settings = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "std_format": {
            "format": "[{levelname}][{threadName}][{processName}] {asctime} | {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": logging.DEBUG,
            "formatter": "std_format",
        }
    },
    "loggers": {f"{LOGGER_NAME}": {"level": logging.DEBUG, "handlers": ["console"]}},
}

# Setting up the logger to log to the console.
logging.config.dictConfig(logger_settings)
logger = logging.getLogger(LOGGER_NAME)
