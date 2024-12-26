import logging
from dbridge.logging import get_logger


def test_logger_name():
    name = "test_logger_name"
    logger = get_logger(name, "INFO")
    assert logger.name == name


def test_logger_level():
    name = "test_logger_level"
    level = "INFO"
    logger = get_logger(name, level)
    assert logger.level == getattr(logging, level)
