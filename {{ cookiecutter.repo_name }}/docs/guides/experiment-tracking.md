# Experiment tracking

The project uses [MLflow](https://mlflow.org/docs/latest/) to track runs: parameters, metrics, configs and models.

## Tracking store

The default tracking store is a local SQLite database: `sqlite:///mlflow.db`. The path is relative to the current
working directory, so run the commands from the project root. Git ignores `mlflow.db` and `mlartifacts/`.

To use a different store (for example a shared MLflow server), set the tracking URI (see "Priority of the settings"
below).

## MLflow UI

Start the UI:

```shell
make mlflow-ui
```

Then open <http://127.0.0.1:5000>. The target uses `MLFLOW_TRACKING_URI` from the shell. The default is
`sqlite:///mlflow.db`. The target does not read `.env`.

## Delete runs

When you delete a run or an experiment in the UI, MLflow only marks it as deleted. To remove the deleted runs and
experiments permanently, run:

```shell
make mlflow-gc
```

## Priority of the settings

The project reads the MLflow settings from the `mlflow` settings section
(`{{ cookiecutter.package_name }}.core.settings`):

- `MLFLOW__TRACKING_URI` (default `sqlite:///mlflow.db`).
- `MLFLOW__EXPERIMENT_NAME` (default: not set).

You can set these values in `.env` or as environment variables.

MLflow itself reads `MLFLOW_TRACKING_URI` and `MLFLOW_EXPERIMENT_NAME` (one underscore). Managed platforms (for example
Azure ML) set these variables in their jobs. The helpers in `{{ cookiecutter.package_name }}.utils.mlflow` give these
variables priority:

1. The real `MLFLOW_TRACKING_URI` or `MLFLOW_EXPERIMENT_NAME` environment variable, if it is set.
2. The value from the settings (`MLFLOW__TRACKING_URI` or `MLFLOW__EXPERIMENT_NAME`, from the environment or `.env`).
3. The default: `sqlite:///mlflow.db`, and the experiment name `{{ cookiecutter.package_name }}`
    (`consts.tracking.DEFAULT_EXPERIMENT_NAME`).

Use the helpers when you start a run:

```python
import mlflow

from {{ cookiecutter.package_name }} import consts
from {{ cookiecutter.package_name }}.core.settings import settings
from {{ cookiecutter.package_name }}.utils.mlflow import resolve_experiment_name, resolve_tracking_uri

mlflow.set_tracking_uri(resolve_tracking_uri(settings.mlflow.tracking_uri))
mlflow.set_experiment(
    resolve_experiment_name(settings.mlflow.experiment_name or consts.tracking.DEFAULT_EXPERIMENT_NAME)
)
```

## Utilities

`{{ cookiecutter.package_name }}.utils.mlflow` has these functions:

- `resolve_tracking_uri(default)`: return `MLFLOW_TRACKING_URI` if it is set, otherwise `default`.
- `resolve_experiment_name(default)`: return `MLFLOW_EXPERIMENT_NAME` if it is set, otherwise `default`. The
    function does not change the environment.
- `run_id_from_context()`: return `MLFLOW_RUN_ID` if it is set, otherwise `None`.
- `get_latest_run_id(experiment_name, tracking_uri=None)`: return the ID of the most recent run of an experiment.
- `to_mlflow_params(values, sep=".")`: flatten a nested dictionary to parameters for `mlflow.log_params`.
- `log_config_artifact(config, artifact_file="config/config.yaml")`: log a config as a YAML artifact of the active
    run.

For the full API, read the [utils API reference](../api_ref/utils.md).
{%- if cookiecutter.ml_stack == "lightning" %}

## LightningCLI runs

The `lightning` CLI command uses `MLFlowLogger`. It gets the tracking URI and the experiment name with the same
priority. The `MLFlowSaveConfigCallback` callback saves the full LightningCLI config as the `config.yaml` artifact of
the run.
{%- endif %}
{%- if cookiecutter.azure_ml == "yes" %}

## Azure ML

In an Azure ML job, Azure ML sets `MLFLOW_TRACKING_URI` and `MLFLOW_EXPERIMENT_NAME`. The runs then go to the
workspace. The `azureml-mlflow` package (a runtime dependency) lets MLflow log to the workspace. Read
[Azure ML](azure-ml.md).
{%- endif %}

## Dev-logs

Write the results of important runs in a dev-log entry. Include the run IDs. Read the
[DEV-LOG intro](../dev-logs/log.md).
