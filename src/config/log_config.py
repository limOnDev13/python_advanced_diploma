dict_config: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "base": {
            "format": "%(filename)s | %(funcName)s | %(name)s | %(levelname)s | %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "base",
        }
    },
    "loggers": {
        "routes_logger": {"level": "DEBUG", "handlers": ["console"], "propagate": True},
        "query_logger": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
    },
}
