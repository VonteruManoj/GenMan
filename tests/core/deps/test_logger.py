import logging

from src.core.deps.logger import get_logger, with_logger


def test_logger(caplog):
    caplog.set_level(logging.DEBUG)

    logger = get_logger(__name__)
    logger.info("Hello World!")

    # Check the number of log records
    assert len(caplog.records) == 1

    # Check the log level
    assert "INFO" in caplog.text

    # Check the log message
    assert "Hello World!" in caplog.text

    # Check the log source
    assert "tests.core.deps.test_logger:test_logger.py" in caplog.text


# ------------------------------
# with_logger
# ------------------------------
def test_with_logger(caplog):
    caplog.set_level(logging.DEBUG)

    @with_logger()
    class TestClass:
        def __init__(self):
            self._logger.info("Hello World!")

    TestClass()

    # Check the number of log records
    assert len(caplog.records) == 1

    # Check the log level
    assert "INFO" in caplog.text

    # Check the log message
    assert "Hello World!" in caplog.text

    # Check the log source
    assert "TestClass:test_logger.py" in caplog.text
