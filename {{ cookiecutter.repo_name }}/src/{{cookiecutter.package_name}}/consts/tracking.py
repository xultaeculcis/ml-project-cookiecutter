"""Experiment tracking (MLflow) consts.

Attributes:
    DEFAULT_TRACKING_URI (str): Local SQLite tracking store, relative to the current working directory.
    DEFAULT_EXPERIMENT_NAME (str): Experiment name used when neither the config nor the environment sets one.

"""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
DEFAULT_TRACKING_URI = "sqlite:///mlflow.db"
DEFAULT_EXPERIMENT_NAME = "{{cookiecutter.package_name}}"
