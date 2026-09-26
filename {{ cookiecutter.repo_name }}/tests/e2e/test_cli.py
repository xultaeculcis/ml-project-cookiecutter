{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parents[2]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [sys.executable, "-m", "{{cookiecutter.package_name}}", *args],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )


def test_help() -> None:
    result = _run_cli("--help")
    assert result.returncode == 0, result.stderr
    assert "train" in result.stdout


def test_train_with_committed_config() -> None:
    result = _run_cli("train", "--config", "configs/train.yaml")
    assert result.returncode == 0, result.stderr
    assert "TODO: implement training" in result.stderr
