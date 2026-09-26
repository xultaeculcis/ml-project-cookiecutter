# Run configs

Run parameters (paths, hyperparameters, seeds, experiment names) go in YAML files in `configs/`. Git tracks these
files, so each run can be repeated from a commit. Secrets do not go in configs. Put secrets in `.env` (read
[Setting up the dev environment](setup-dev-env.md)).

## Files

Each config family has one loader: the code that reads it in the CLI. A family is a directory under `configs/`, or the
file name without `.yaml` for a file directly in `configs/`.

- `configs/train.yaml`: family `train`, validated by `TrainConfig`. Command:
    `{{ cookiecutter.repo_name }} train --config configs/train.yaml`.
- `configs/evaluate.yaml`: family `evaluate`, validated by `EvaluateConfig`. Command:
    `{{ cookiecutter.repo_name }} evaluate --config configs/evaluate.yaml`.
- `configs/predict.yaml`: family `predict`, validated by `PredictConfig`. Command:
    `{{ cookiecutter.repo_name }} predict --config configs/predict.yaml`.
{%- if cookiecutter.ml_stack == "lightning" %}
- `configs/lightning/*.yaml`: family `lightning`, read by LightningCLI. Command:
    `{{ cookiecutter.repo_name }} lightning fit --config configs/lightning/fit.yaml`.
{%- endif %}

`configs/README.md` has the same list. Keep both lists up to date.

## Validation

The config models are in `{{ cookiecutter.package_name }}.core.configs`. They are pydantic models:

- `BaseConfig` rejects unknown keys (`extra="forbid"`). A typo in a key fails when the config loads.
- `BaseConfig.from_yaml(path)` loads and validates a YAML file.
- `BaseConfig.to_dict()` returns a JSON-compatible dictionary, for example to log the config to MLflow.
- `TrackingConfig` adds the MLflow fields `experiment_name` and `run_name`, and the `seed` field.

Example:

```python
from {{ cookiecutter.package_name }}.core.configs import TrainConfig

config = TrainConfig.from_yaml("configs/train.yaml")
config.max_epochs  # 10
```

## The load-all test

`tests/unit/test_configs.py` loads every `*.yaml` and `*.yml` file under `configs/` with the loader of its family.
The `CONFIG_LOADERS` dictionary in the test maps each family to its loader. A file in a family without a loader fails
the test. The test is not skipped. Thus a config that the code cannot read cannot be merged.

## Add a config

- To add a variant of an existing family, add a file in a directory with the family name, for example
    `configs/train/baseline.yaml` (family `train`). No code change is necessary.
- To add a new family:
    1. Add a pydantic model to `{{ cookiecutter.package_name }}.core.configs`. Subclass `BaseConfig`, or
        `TrackingConfig` if the command creates an MLflow run.
    2. Add the command that reads the config (read [Command-line interface](cli.md)).
    3. Add the family and its loader to `CONFIG_LOADERS` in `tests/unit/test_configs.py`.
    4. Add the family to `configs/README.md`.

## Log the config of a run

Log the config with each MLflow run, so that you can repeat the run:

```python
import mlflow

from {{ cookiecutter.package_name }}.utils.mlflow import log_config_artifact, to_mlflow_params

with mlflow.start_run(run_name=config.run_name):
    mlflow.log_params(to_mlflow_params(config.to_dict()))
    log_config_artifact(config.to_dict())
```
