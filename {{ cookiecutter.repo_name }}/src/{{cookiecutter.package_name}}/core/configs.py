"""Run configuration models for the CLI commands.

Each command reads one YAML file and validates it with one of these models. Unknown keys are an error, so a typo in
a config fails at load time. `configs/README.md` lists which model reads which file, and
`tests/unit/test_configs.py` loads every committed config.

Examples:
    ```python
    from {{cookiecutter.package_name}}.core.configs import TrainConfig

    config = TrainConfig.from_yaml("configs/train.yaml")
    print(config.max_epochs)
    ```

"""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
from pathlib import Path
from typing import Any, Self

import yaml
from pydantic import BaseModel, ConfigDict, Field

from {{cookiecutter.package_name}} import consts


class BaseConfig(BaseModel):
    """Base class for run configs: strict keys and YAML loading."""

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def from_yaml(cls, path: str | Path) -> Self:
        """Load and validate a config from a YAML file.

        Args:
            path: Path to the YAML file.

        Returns:
            The validated config.

        Raises:
            pydantic.ValidationError: If the content does not match the model.

        """
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        """Return the config as a JSON-compatible dictionary, for example to log it to MLflow.

        Returns:
            The config as a dictionary.

        """
        return self.model_dump(mode="json")


class TrackingConfig(BaseConfig):
    """Fields shared by all configs that create an MLflow run."""

    experiment_name: str | None = Field(
        default=None,
        description="MLflow experiment name. If not set, the settings or the environment decide.",
    )
    run_name: str | None = Field(default=None, description="MLflow run name. If not set, MLflow generates one.")
    seed: int = Field(default=consts.reproducibility.SEED, description="Random seed for `seed_everything`.")


class TrainConfig(TrackingConfig):
    """Config for the `train` command."""

    data_dir: Path = Field(default=Path("data/processed"), description="Directory with the training data.")
    max_epochs: int = Field(default=10, gt=0)
    batch_size: int = Field(default=32, gt=0)
    learning_rate: float = Field(default=1e-3, gt=0.0)


class EvaluateConfig(TrackingConfig):
    """Config for the `evaluate` command."""

    model_uri: str = Field(description="MLflow model URI, for example `runs:/<run_id>/model`.")
    data_dir: Path = Field(default=Path("data/processed"), description="Directory with the evaluation data.")


class PredictConfig(BaseConfig):
    """Config for the `predict` command."""

    model_uri: str = Field(description="MLflow model URI, for example `models:/<name>/<version>`.")
    input_path: Path = Field(description="File or directory with the input data.")
    output_path: Path = Field(description="Where to write the predictions.")
