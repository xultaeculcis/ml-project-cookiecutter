from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from {{cookiecutter.package_name}} import consts
from {{cookiecutter.package_name}}.utils.logging import get_logger, timing_context

_NAME_TO_LEVEL = {
    "CRITICAL": logging.CRITICAL,
    "FATAL": logging.FATAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}
_LOGGER_NAME = "test_logger"


class DummyError(Exception): ...


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
    assert formatter._fmt == expected_format  # type: ignore[union-attr] # noqa: SLF001


def test_timed_decorator_functionality() -> None:
    @timing_context("test_func")
    def test_func(x: int, y: int) -> int:
        return x + y * y

    # Test that the function still works as expected
    assert test_func(1, 2) == 5  # noqa: PLR2004


@patch("{{cookiecutter.package_name}}.utils.logging.time.time", MagicMock(side_effect=[100.0, 101.0]))
@patch("logging.Logger.info")
def test_timed_decorator_logging(mock_info: MagicMock) -> None:
    @timing_context("test_func")
    def test_func(x: int, y: int) -> int:
        return x + y * y

    test_func(1, 2)

    assert mock_info.call_count == 2  # noqa: PLR2004
    start_call, end_call = mock_info.call_args_list
    assert "is running" in start_call[0][0]
    assert "ran in" in end_call[0][0]


@patch("{{cookiecutter.package_name}}.utils.logging.time.time", MagicMock(side_effect=[100.0, 101.0]))
@patch("logging.Logger.info")
def test_timed_with_block_logging(mock_info: MagicMock) -> None:
    def test_func(x: int, y: int) -> int:
        return x + y * y

    with timing_context("test_func"):
        test_func(1, 2)

    assert mock_info.call_count == 2  # noqa: PLR2004
    start_call, end_call = mock_info.call_args_list
    assert "is running" in start_call[0][0]
    assert "ran in" in end_call[0][0]


@patch("{{cookiecutter.package_name}}.utils.logging.time.time", MagicMock(side_effect=[100.0, 101.0]))
@patch("logging.Logger.info")
def test_timed_block_logging_on_exception(mock_info: MagicMock) -> None:
    def test_func() -> int:
        msg = "test"
        raise DummyError(msg)

    with pytest.raises(DummyError), timing_context("test_func"):
        test_func()

    assert mock_info.call_count == 2  # noqa: PLR2004
    start_call, end_call = mock_info.call_args_list
    assert "is running" in start_call[0][0]
    assert "ran in" in end_call[0][0]


@patch("{{cookiecutter.package_name}}.utils.logging.time.time", MagicMock(side_effect=[100.0, 101.0]))
@patch("logging.Logger.info")
def test_timed_decorator_logging_on_exception(mock_info: MagicMock) -> None:
    @timing_context("test_func")
    def test_func() -> int:
        msg = "test"
        raise DummyError(msg)

    with pytest.raises(DummyError):
        test_func()

    assert mock_info.call_count == 2  # noqa: PLR2004
    start_call, end_call = mock_info.call_args_list
    assert "is running" in start_call[0][0]
    assert "ran in" in end_call[0][0]
