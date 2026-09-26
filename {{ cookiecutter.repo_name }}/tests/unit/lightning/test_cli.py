{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
from pathlib import Path

import pytest
from click.testing import CliRunner
from mlflow import MlflowClient

from {{cookiecutter.package_name}}.cli.entrypoint import main
from {{cookiecutter.package_name}}.lightning.cli import run

FIT_CONFIG = Path(__file__).parents[3] / "configs" / "lightning" / "fit.yaml"


@pytest.fixture
def tracking_uri(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.chdir(tmp_path)
    uri = f"sqlite:///{(tmp_path / 'mlflow.db').as_posix()}"
    monkeypatch.setenv("MLFLOW_TRACKING_URI", uri)
    monkeypatch.setenv("MLFLOW_EXPERIMENT_NAME", "lightning-test")
    monkeypatch.delenv("MLFLOW_RUN_ID", raising=False)
    return uri


def test_help_is_passed_to_lightning_cli() -> None:
    result = CliRunner().invoke(main, ["lightning", "--help"])
    assert result.exit_code == 0
    assert "fit" in result.output


@pytest.mark.slow
def test_fit_logs_metrics_and_config_to_mlflow(tracking_uri: str) -> None:
    cli = run(["fit", "--config", str(FIT_CONFIG)])

    assert cli.trainer.state.finished
    client = MlflowClient(tracking_uri=tracking_uri)
    experiment = client.get_experiment_by_name("lightning-test")
    assert experiment is not None
    (mlflow_run,) = client.search_runs([experiment.experiment_id])
    assert "train/loss" in mlflow_run.data.metrics
    assert "config.yaml" in {artifact.path for artifact in client.list_artifacts(mlflow_run.info.run_id)}
