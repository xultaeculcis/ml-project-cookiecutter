import logging
import pytest

from {{cookiecutter.src_dir_name}} import consts
from {{cookiecutter.src_dir_name}}.utils.logging import get_logger

_NAME_TO_LEVEL = {
    "CRITICAL": logging.CRITICAL,
    "FATAL": logging.FATAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}
_LOGGER_NAME = "test_logger"

def test_should_make_logger_with_specified_name() -> None:
    logger = get_logger(_LOGGER_NAME, "INFO")
    assert logger.name == _LOGGER_NAME


@pytest.mark.parametrize("level", list(_NAME_TO_LEVEL.keys()))
def test_should_make_logger_with_specified_level_names(level: str) -> None:
    logger = get_logger(_LOGGER_NAME, level)
    assert logger.level == _NAME_TO_LEVEL[level]


@pytest.mark.parametrize("level", list(_NAME_TO_LEVEL.values()))
def test_should_make_logger_with_specified_level_codes(level: int) -> None:
    logger = get_logger(_LOGGER_NAME, level)
    assert logger.level == level


def test_default_log_level() -> None:
    logger = get_logger(_LOGGER_NAME)
    assert logger.level == logging.INFO


def test_custom_log_level() -> None:
    logger = get_logger(_LOGGER_NAME, logging.DEBUG)
    assert logger.level == logging.DEBUG


def test_stream_handler_added() -> None:
    logger = get_logger(_LOGGER_NAME)
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_formatter_configuration() -> None:
    logger = get_logger(_LOGGER_NAME)
    formatter = logger.handlers[0].formatter
    expected_format = consts.logging.FORMAT
    assert formatter._fmt == expected_format
