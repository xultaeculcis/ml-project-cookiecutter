"""Every committed config under `configs/` loads through the loader that reads it in the CLI.

A config family is the first directory under `configs/`, or the file name without `.yaml` for files directly in
`configs/`. `CONFIG_LOADERS` must name every family: a config in an unknown family fails the test instead of being
skipped. When you add a family, add its loader here and a row to `configs/README.md`.
"""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from {{cookiecutter.package_name}}.core.configs import EvaluateConfig, PredictConfig, TrainConfig
{%- if cookiecutter.ml_stack == "lightning" %}
from {{cookiecutter.package_name}}.lightning.cli import run as run_lightning_cli
{%- endif %}

if TYPE_CHECKING:
    from collections.abc import Callable

CONFIGS_DIR = Path(__file__).parents[2] / "configs"
CONFIG_FILES = sorted(CONFIGS_DIR.rglob("*.y*ml"))
{%- if cookiecutter.ml_stack == "lightning" %}


def load_lightning_config(path: Path) -> object:
    """Parse the config and create the trainer, model and data module, as `lightning fit` does, without training."""
    return run_lightning_cli(["--config", str(path)], run_subcommand=False).config
{%- endif %}


CONFIG_LOADERS: dict[str, Callable[[Path], object]] = {
    "train": TrainConfig.from_yaml,
    "evaluate": EvaluateConfig.from_yaml,
    "predict": PredictConfig.from_yaml,
{%- if cookiecutter.ml_stack == "lightning" %}
    "lightning": load_lightning_config,
{%- endif %}
}


def config_family(path: Path) -> str:
    relative = path.relative_to(CONFIGS_DIR)
    return relative.parts[0] if len(relative.parts) > 1 else relative.stem


def test_configs_exist() -> None:
    assert CONFIG_FILES, f"No configs found in {CONFIGS_DIR}"


@pytest.mark.parametrize("path", CONFIG_FILES, ids=lambda p: p.relative_to(CONFIGS_DIR).as_posix())
def test_config_loads(path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Keep files that a loader may create (MLflow store, Lightning output) out of the project.
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", f"sqlite:///{(tmp_path / 'mlflow.db').as_posix()}")
    monkeypatch.setenv("MLFLOW_EXPERIMENT_NAME", "test-configs")

    family = config_family(path)
    assert family in CONFIG_LOADERS, f"No loader for config family {family!r}. Add one to CONFIG_LOADERS."
    assert CONFIG_LOADERS[family](path) is not None
