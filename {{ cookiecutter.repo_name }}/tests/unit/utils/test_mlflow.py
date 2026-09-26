{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import os
from datetime import date
from pathlib import Path
from unittest.mock import patch

import mlflow
import pytest
import yaml
from mlflow import MlflowClient

from {{cookiecutter.package_name}}.utils.mlflow import (
    MLflowExperimentNotFoundError,
    MLflowRunsNotFoundError,
    get_latest_run_id,
    log_config_artifact,
    resolve_experiment_name,
    resolve_tracking_uri,
    run_id_from_context,
    to_mlflow_params,
)


@pytest.fixture
def tracking_uri(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    """Use a SQLite tracking store in a temporary directory. Artifacts go to `./mlruns` in the same directory."""
    monkeypatch.chdir(tmp_path)
    uri = f"sqlite:///{(tmp_path / 'mlflow.db').as_posix()}"
    monkeypatch.setenv("MLFLOW_TRACKING_URI", uri)
    return uri


def test_resolve_experiment_name_env_set() -> None:
    with patch.dict(os.environ, {"MLFLOW_EXPERIMENT_NAME": "env-defined-mlflow-experiment-name"}):
        result = resolve_experiment_name("default-mlflow-experiment-name")
        assert result == "env-defined-mlflow-experiment-name"


def test_resolve_experiment_name_env_not_set() -> None:
    with patch.dict(os.environ, {}, clear=True):
        result = resolve_experiment_name("default-mlflow-experiment-name")
        assert result == "default-mlflow-experiment-name"
        # The function must not change the environment.
        assert "MLFLOW_EXPERIMENT_NAME" not in os.environ


def test_resolve_experiment_name_env_unset_then_set() -> None:
    with patch.dict(os.environ, {}, clear=True):
        assert resolve_experiment_name("default-mlflow-experiment-name") == "default-mlflow-experiment-name"
        os.environ["MLFLOW_EXPERIMENT_NAME"] = "new-env-defined-mlflow-experiment-name"
        assert resolve_experiment_name("different-mlflow-experiment-name") == "new-env-defined-mlflow-experiment-name"


def test_run_id_from_context_set() -> None:
    with patch.dict(os.environ, {"MLFLOW_RUN_ID": "1234"}):
        result = run_id_from_context()
        assert result == "1234"


def test_run_id_from_context_not_set() -> None:
    with patch.dict(os.environ, {}, clear=True):
        result = run_id_from_context()
        assert result is None


def test_resolve_tracking_uri_prefers_env_var() -> None:
    with patch.dict(os.environ, {"MLFLOW_TRACKING_URI": "http://mlflow.example:5000"}):
        assert resolve_tracking_uri("sqlite:///mlflow.db") == "http://mlflow.example:5000"


def test_resolve_tracking_uri_uses_default_when_env_var_is_not_set() -> None:
    with patch.dict(os.environ, {}, clear=True):
        assert resolve_tracking_uri("sqlite:///mlflow.db") == "sqlite:///mlflow.db"
        assert "MLFLOW_TRACKING_URI" not in os.environ


def test_to_mlflow_params_flattens_nested_dicts_and_encodes_other_values() -> None:
    params = to_mlflow_params(
        {
            "lr": 0.001,
            "epochs": 10,
            "name": "baseline",
            "enabled": True,
            "missing": None,
            "optimizer": {"name": "adam", "betas": [0.9, 0.999]},
            "data_dir": Path("data/processed"),
            "since": date(2024, 1, 2),
        }
    )
    assert params == {
        "lr": 0.001,
        "epochs": 10,
        "name": "baseline",
        "enabled": True,
        "missing": None,
        "optimizer.name": "adam",
        "optimizer.betas": "[0.9, 0.999]",
        "data_dir": '"data/processed"',
        "since": '"2024-01-02"',
    }


def test_to_mlflow_params_custom_separator() -> None:
    assert to_mlflow_params({"a": {"b": {"c": 1}}}, sep="/") == {"a/b/c": 1}


def test_get_latest_run_id_returns_most_recent_run(tracking_uri: str) -> None:
    client = MlflowClient(tracking_uri=tracking_uri)
    experiment_id = client.create_experiment("exp")
    client.create_run(experiment_id, start_time=1_000)
    latest = client.create_run(experiment_id, start_time=2_000)
    client.create_run(experiment_id, start_time=1_500)

    assert get_latest_run_id("exp", tracking_uri=tracking_uri) == latest.info.run_id


def test_get_latest_run_id_unknown_experiment(tracking_uri: str) -> None:
    with pytest.raises(MLflowExperimentNotFoundError, match="no-such-exp"):
        get_latest_run_id("no-such-exp", tracking_uri=tracking_uri)


def test_get_latest_run_id_experiment_without_runs(tracking_uri: str) -> None:
    MlflowClient(tracking_uri=tracking_uri).create_experiment("empty")
    with pytest.raises(MLflowRunsNotFoundError, match="empty"):
        get_latest_run_id("empty", tracking_uri=tracking_uri)


@pytest.mark.usefixtures("tracking_uri")
def test_log_config_artifact_writes_yaml() -> None:
    config = {"seed": 42, "data_dir": Path("data/processed"), "optimizer": {"name": "adam"}}
    with mlflow.start_run() as run:
        log_config_artifact(config)

    text = mlflow.artifacts.load_text(f"runs:/{run.info.run_id}/config/config.yaml")
    assert yaml.safe_load(text) == {"seed": 42, "data_dir": "data/processed", "optimizer": {"name": "adam"}}
