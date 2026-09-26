"""Logging utils."""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import contextlib
import logging
import sys
import time
from typing import TYPE_CHECKING, TextIO

from {{cookiecutter.package_name}} import consts

if TYPE_CHECKING:
    from collections.abc import Generator

PACKAGE_LOGGER_NAME = "{{cookiecutter.package_name}}"
_HANDLER_NAME = f"{PACKAGE_LOGGER_NAME}.stderr"


class _StderrHandler(logging.StreamHandler):  # type: ignore[type-arg]
    """Stream handler that writes to the current `sys.stderr`.

    A plain `StreamHandler` keeps the stream from the time it was created. Test runners (for example
    `click.testing.CliRunner`) replace `sys.stderr` and close their stream later.
    """

    @property
    def stream(self) -> TextIO:
        return sys.stderr

    @stream.setter
    def stream(self, value: TextIO) -> None:
        """Ignore the stream that `StreamHandler.__init__` sets."""


def get_logger(name: str, log_level: int | str | None = None) -> logging.Logger:
    """Return a logger in the package namespace.

    Use `get_logger(__name__)` in each module. The logger has no handler of its own. Its records go to the package
    logger (`"{{cookiecutter.package_name}}"`), which `configure_logging` sets up. A name outside the package
    namespace gets the package name as a prefix.

    Args:
        name: The name for the logger, usually `__name__`.
        log_level: The log level of this logger. If `None`, the logger uses the level of the package logger.

    Returns:
        The logger.

    """
    if name != PACKAGE_LOGGER_NAME and not name.startswith(f"{PACKAGE_LOGGER_NAME}."):
        name = f"{PACKAGE_LOGGER_NAME}.{name}"
    logger = logging.getLogger(name)
    if log_level is not None:
        logger.setLevel(log_level.upper() if isinstance(log_level, str) else log_level)
    return logger


def configure_logging(level: int | str = logging.INFO) -> logging.Logger:
    """Set the level of the package logger and add one stderr handler with `consts.logging.FORMAT`.

    Call it once at the start of a program, for example in the CLI. More calls change only the level.

    Args:
        level: The log level for all loggers in the package, for example `"DEBUG"` or `logging.INFO`.

    Returns:
        The package logger.

    """
    logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    logger.setLevel(level.upper() if isinstance(level, str) else level)
    if not any(handler.get_name() == _HANDLER_NAME for handler in logger.handlers):
        handler = _StderrHandler()
        handler.set_name(_HANDLER_NAME)
        handler.setFormatter(logging.Formatter(fmt=consts.logging.FORMAT))
        logger.addHandler(handler)
    return logger


_timed_logger = get_logger(__name__)


@contextlib.contextmanager
def timing_context(name: str) -> Generator[None]:
    """Prints the execution time for the decorated function.

    Notes:
        Can also act as a context manager.

    Args:
        name: The name of the wrapped execution block.

    Returns:
        A context manager that prints the execution time.

    """
    _timed_logger.info("%(func_name)s is running...", {"func_name": name})
    t0 = time.monotonic()
    try:
        yield
    finally:
        t1 = time.monotonic()
        _timed_logger.info(
            "%(func_name)s ran in %(execution_time)s",
            {
                "func_name": name,
                "execution_time": f"{(t1 - t0):.4f}",
            },
        )
