{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from {{cookiecutter.package_name}}.cli import entrypoint
from {{cookiecutter.package_name}}.cli.entrypoint import main

CONFIGS_DIR = Path(__file__).parents[2] / "configs"


@pytest.mark.parametrize(
    ("command", "message"),
    [
        ("train", "TODO: implement training"),
        ("evaluate", "TODO: implement evaluation"),
        ("predict", "TODO: implement prediction"),
    ],
)
def test_command_runs_with_committed_config(command: str, message: str, monkeypatch: pytest.MonkeyPatch) -> None:
    info = MagicMock()
    monkeypatch.setattr(entrypoint._logger, "info", info)  # noqa: SLF001

    result = CliRunner().invoke(main, [command, "--config", str(CONFIGS_DIR / f"{command}.yaml")])

    assert result.exit_code == 0, result.output
    info.assert_any_call(message)
