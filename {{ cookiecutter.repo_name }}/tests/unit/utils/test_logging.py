{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import logging
import sys
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from {{cookiecutter.package_name}} import consts
from {{cookiecutter.package_name}}.utils.logging import PACKAGE_LOGGER_NAME, configure_logging, get_logger, timing_context

if TYPE_CHECKING:
    from collections.abc import Iterator

_NAME_TO_LEVEL = {
    "CRITICAL": logging.CRITICAL,
    "FATAL": logging.FATAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}
_LOGGER_NAME = f"{PACKAGE_LOGGER_NAME}.test_logger"


class DummyError(Exception): ...


@pytest.fixture(autouse=True)
def _restore_package_logger() -> Iterator[None]:
    """Restore the level and the handlers of the package logger and the test logger after each test."""
    package_logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    test_logger = logging.getLogger(_LOGGER_NAME)
    saved = (package_logger.level, list(package_logger.handlers), test_logger.level)
    yield
    package_logger.setLevel(saved[0])
    package_logger.handlers[:] = saved[1]
    test_logger.setLevel(saved[2])


def test_should_make_logger_with_specified_name() -> None:
    logger = get_logger(_LOGGER_NAME)
    assert logger.name == _LOGGER_NAME


def test_name_outside_package_gets_prefix() -> None:
    assert get_logger("other").name == f"{PACKAGE_LOGGER_NAME}.other"


def test_logger_has_no_handler_and_propagates() -> None:
    logger = get_logger(_LOGGER_NAME)
    assert logger.handlers == []
    assert logger.propagate
    assert logger.level == logging.NOTSET


@pytest.mark.parametrize("level", list(_NAME_TO_LEVEL.keys()))
def test_should_make_logger_with_specified_level_names(level: str) -> None:
    logger = get_logger(_LOGGER_NAME, level.lower())
    assert logger.level == _NAME_TO_LEVEL[level]


@pytest.mark.parametrize("level", list(_NAME_TO_LEVEL.values()))
def test_should_make_logger_with_specified_level_codes(level: int) -> None:
    logger = get_logger(_LOGGER_NAME, level)
    assert logger.level == level


def test_configure_logging_is_idempotent() -> None:
    configure_logging("INFO")
    package_logger = configure_logging("DEBUG")
    handlers = [h for h in package_logger.handlers if h.get_name() == f"{PACKAGE_LOGGER_NAME}.stderr"]
    assert len(handlers) == 1
    assert package_logger.level == logging.DEBUG
    assert handlers[0].formatter is not None
    assert handlers[0].formatter._fmt == consts.logging.FORMAT  # noqa: SLF001


def test_configure_logging_level_reaches_module_loggers(caplog: pytest.LogCaptureFixture) -> None:
    configure_logging("DEBUG")
    with caplog.at_level(logging.DEBUG):
        get_logger(_LOGGER_NAME).debug("debug message")
    assert "debug message" in caplog.text

    configure_logging("WARNING")
    caplog.clear()
    get_logger(_LOGGER_NAME).info("info message")
    assert "info message" not in caplog.text


def test_handler_writes_to_current_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO")
    get_logger(_LOGGER_NAME).info("to stderr")
    assert "to stderr" in capsys.readouterr().err
    handler = next(h for h in logging.getLogger(PACKAGE_LOGGER_NAME).handlers if h.get_name().endswith(".stderr"))
    assert handler.stream is sys.stderr  # type: ignore[attr-defined]


def test_timed_decorator_functionality() -> None:
    @timing_context("test_func")
    def test_func(x: int, y: int) -> int:
        return x + y * y

    # Test that the function still works as expected
    assert test_func(1, 2) == 5


@patch("{{cookiecutter.package_name}}.utils.logging.time.monotonic", MagicMock(side_effect=[100.0, 101.5]))
@patch("logging.Logger.info")
def test_timed_decorator_logging(mock_info: MagicMock) -> None:
    @timing_context("test_func")
    def test_func(x: int, y: int) -> int:
        return x + y * y

    test_func(1, 2)

    assert mock_info.call_count == 2
    start_call, end_call = mock_info.call_args_list
    assert "is running" in start_call.args[0]
    assert "ran in" in end_call.args[0]
    assert end_call.args[1] == {"func_name": "test_func", "execution_time": "1.5000"}


@patch("{{cookiecutter.package_name}}.utils.logging.time.monotonic", MagicMock(side_effect=[100.0, 101.5]))
@patch("logging.Logger.info")
def test_timed_with_block_logging(mock_info: MagicMock) -> None:
    def test_func(x: int, y: int) -> int:
        return x + y * y

    with timing_context("test_func"):
        test_func(1, 2)

    assert mock_info.call_count == 2
    start_call, end_call = mock_info.call_args_list
    assert "is running" in start_call.args[0]
    assert "ran in" in end_call.args[0]
    assert end_call.args[1] == {"func_name": "test_func", "execution_time": "1.5000"}


@patch("{{cookiecutter.package_name}}.utils.logging.time.monotonic", MagicMock(side_effect=[100.0, 101.5]))
@patch("logging.Logger.info")
def test_timed_block_logging_on_exception(mock_info: MagicMock) -> None:
    def test_func() -> int:
        msg = "test"
        raise DummyError(msg)

    with pytest.raises(DummyError), timing_context("test_func"):
        test_func()

    assert mock_info.call_count == 2
    start_call, end_call = mock_info.call_args_list
    assert "is running" in start_call.args[0]
    assert "ran in" in end_call.args[0]
    assert end_call.args[1] == {"func_name": "test_func", "execution_time": "1.5000"}


@patch("{{cookiecutter.package_name}}.utils.logging.time.monotonic", MagicMock(side_effect=[100.0, 101.5]))
@patch("logging.Logger.info")
def test_timed_decorator_logging_on_exception(mock_info: MagicMock) -> None:
    @timing_context("test_func")
    def test_func() -> int:
        msg = "test"
        raise DummyError(msg)

    with pytest.raises(DummyError):
        test_func()

    assert mock_info.call_count == 2
    start_call, end_call = mock_info.call_args_list
    assert "is running" in start_call.args[0]
    assert "ran in" in end_call.args[0]
    assert end_call.args[1] == {"func_name": "test_func", "execution_time": "1.5000"}
