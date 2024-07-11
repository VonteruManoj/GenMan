import logging
from functools import lru_cache


@lru_cache()
def get_logger(logger_name: str) -> logging.Logger:
    """Get a logger instance.

    Parameters
    ----------
    logger_name: str
        Name of the logger

    Returns
    -------
    Logger
        Logger instance
    """

    return logging.getLogger(logger_name)


@lru_cache()
def with_logger():
    """Decorator to add a logger to a class.

    Notes
    -----
    The logger is added as a property to the class.
    The property is named "_logger" and is a Logger instance.
    """

    def deco(cls):
        def _get_logger(self) -> logging.Logger:
            return getattr(self, "_logger")

        def _set_logger(self, value: logging.Logger):
            setattr(self, "_logger", value)

        prop = property(_get_logger, _set_logger)
        setattr(cls, "_logger", prop)
        setattr(cls, "_logger", get_logger(cls.__name__))

        return cls

    return deco
