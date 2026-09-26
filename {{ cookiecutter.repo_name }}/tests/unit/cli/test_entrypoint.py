{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import logging
from typing import TYPE_CHECKING

import pytest
from click.testing import CliRunner

from {{cookiecutter.package_name}}.cli import entrypoint
from {{cookiecutter.package_name}}.cli.entrypoint import main
from {{cookiecutter.package_name}}.utils.logging import PACKAGE_LOGGER_NAME

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_help_lists_commands(runner: CliRunner) -> None:
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    for command in ("train", "evaluate", "predict"{% if cookiecutter.ml_stack == "lightning" %}, "lightning"{% endif %}):
        assert command in result.output


@pytest.mark.parametrize("command", ["train", "evaluate", "predict"])
def test_config_is_required(runner: CliRunner, command: str) -> None:
    result = runner.invoke(main, [command])
    assert result.exit_code == 2
    assert "--config" in result.output


def test_missing_config_file(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(main, ["train", "--config", str(tmp_path / "missing.yaml")])
    assert result.exit_code == 2
    assert "does not exist" in result.output


def test_invalid_config_is_a_usage_error(runner: CliRunner, tmp_path: Path) -> None:
    path = tmp_path / "train.yaml"
    path.write_text("unknown_key: 1\n", encoding="utf-8")
    result = runner.invoke(main, ["train", "--config", str(path)])
    assert result.exit_code == 2
    assert "unknown_key" in result.output


def test_log_level_option(runner: CliRunner, tmp_path: Path) -> None:
    package_logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    saved_level, saved_handlers = package_logger.level, list(package_logger.handlers)
    path = tmp_path / "train.yaml"
    path.write_text("seed: 1\n", encoding="utf-8")
    try:
        result = runner.invoke(main, ["--log-level", "debug", "train", "--config", str(path)])
        assert result.exit_code == 0
        assert package_logger.level == logging.DEBUG
        assert entrypoint._logger.getEffectiveLevel() == logging.DEBUG  # noqa: SLF001
    finally:
        package_logger.setLevel(saved_level)
        package_logger.handlers[:] = saved_handlers
