from __future__ import annotations

import os


def resolve_experiment_name(default_experiment_name: str) -> str:
    if os.environ.get("MLFLOW_EXPERIMENT_NAME", None) is None:
        os.environ["MLFLOW_EXPERIMENT_NAME"] = default_experiment_name
    return os.environ["MLFLOW_EXPERIMENT_NAME"]


def run_id_from_context() -> str | None:
    return os.environ.get("MLFLOW_RUN_ID", None)
