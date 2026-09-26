"""MLflow utils."""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import json
import os
from typing import Any

import mlflow
import yaml
from mlflow import MlflowClient

from {{cookiecutter.package_name}}.utils.serialization import JsonEncoder


class MLflowUtilsError(RuntimeError):
    """Base exception for MLflow util failures."""


class MLflowExperimentNotFoundError(MLflowUtilsError):
    """Raised when an MLflow experiment with the given name does not exist."""


class MLflowRunsNotFoundError(MLflowUtilsError):
    """Raised when an MLflow experiment has no runs."""


def resolve_experiment_name(default_experiment_name: str) -> str:
    """Resolves the MLflow experiment name.

    `"MLFLOW_EXPERIMENT_NAME"` has priority, because Azure ML and other managed platforms set it for their jobs.
    Otherwise, the default passed as an argument is used. The function does not change the environment.

    Args:
        default_experiment_name: The experiment name to use if the environment variable is not set.

    Returns:
        The resolved experiment name.

    Examples:
        When `MLFLOW_EXPERIMENT_NAME` is not set:

        >>> resolve_experiment_name("custom-mlflow-experiment-name")
        'custom-mlflow-experiment-name'

    """
    return os.environ.get("MLFLOW_EXPERIMENT_NAME") or default_experiment_name


def resolve_tracking_uri(default_tracking_uri: str) -> str:
    """Resolves the MLflow tracking URI.

    `"MLFLOW_TRACKING_URI"` has priority, because Azure ML and other managed platforms set it for their jobs.
    Otherwise, the default passed as an argument is used, for example `settings.mlflow.tracking_uri`.

    Args:
        default_tracking_uri: The tracking URI to use if the environment variable is not set.

    Returns:
        The resolved tracking URI.

    """
    return os.environ.get("MLFLOW_TRACKING_URI") or default_tracking_uri


def run_id_from_context() -> str | None:
    """Resolves the MLflow Run ID from the context.

    Returns:
        The MLflow Run ID based on `"MLFLOW_RUN_ID"` environment variable. If not set, returns `None`.

    """
    return os.environ.get("MLFLOW_RUN_ID", None)


def get_latest_run_id(experiment_name: str, tracking_uri: str | None = None) -> str:
    """Return the ID of the most recently started run in an experiment.

    Args:
        experiment_name: The name of the experiment.
        tracking_uri: The tracking URI. If `None`, MLflow uses its current tracking URI.

    Returns:
        The run ID.

    Raises:
        MLflowExperimentNotFoundError: If the experiment does not exist.
        MLflowRunsNotFoundError: If the experiment has no runs.

    """
    client = MlflowClient(tracking_uri=tracking_uri)
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        msg = f"Experiment '{experiment_name}' not found"
        raise MLflowExperimentNotFoundError(msg)

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["attributes.start_time DESC"],
        max_results=1,
    )
    if not runs:
        msg = f"No runs found in experiment '{experiment_name}'"
        raise MLflowRunsNotFoundError(msg)
    return str(runs[0].info.run_id)


def to_mlflow_params(values: dict[str, Any], *, sep: str = ".") -> dict[str, Any]:
    """Convert a (nested) dictionary to MLflow parameters.

    Nested dictionaries are flattened with `sep` between the keys. Scalars stay as they are. Other values (lists,
    paths, dates and so on) are converted to JSON strings.

    Args:
        values: The dictionary to convert.
        sep: The separator between nested keys.

    Returns:
        A flat dictionary that `mlflow.log_params` accepts.

    Examples:
        >>> to_mlflow_params({"optimizer": {"name": "adam", "lr": 0.001}, "layers": [64, 32]})
        {'optimizer.name': 'adam', 'optimizer.lr': 0.001, 'layers': '[64, 32]'}

    """
    params: dict[str, Any] = {}
    for key, value in values.items():
        if isinstance(value, dict):
            nested = to_mlflow_params(value, sep=sep)
            params.update({f"{key}{sep}{nested_key}": nested_value for nested_key, nested_value in nested.items()})
        elif value is None or isinstance(value, bool | int | float | str):
            params[key] = value
        else:
            params[key] = json.dumps(value, cls=JsonEncoder, sort_keys=True)
    return params


def log_config_artifact(config: dict[str, Any], artifact_file: str = "config/config.yaml") -> None:
    """Log a config as a YAML artifact of the active MLflow run.

    Args:
        config: The config. Use `config.to_dict()` for a pydantic config from `core.configs`.
        artifact_file: The artifact path, relative to the run's artifact root.

    """
    # The JSON round trip converts paths, dates and numpy values to types that `yaml.safe_dump` accepts.
    serializable = json.loads(json.dumps(config, cls=JsonEncoder))
    mlflow.log_text(yaml.safe_dump(serializable, sort_keys=False), artifact_file=artifact_file)
