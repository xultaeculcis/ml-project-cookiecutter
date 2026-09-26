# Azure ML

Definitions to run the project CLI as Azure ML jobs. The `make aml-*` targets in `mk/aml.mk` wrap the `az ml` commands.

- `environments/env.yaml`: the job environment, a Python image with uv.{% if cookiecutter.docker == "yes" %} A commented
    alternative builds the environment from the project `Dockerfile`.{% endif %} Target: `make aml-env-create`.
- `compute/cpu-cluster.yaml`: a CPU cluster that scales to zero. Target: `make aml-compute-create`.
- `components/train.yaml`: a command component that runs `{{cookiecutter.repo_name}} train --config <config>`.
    Target: `make aml-component-create`.
- `pipelines/train-pipeline.yaml`: a pipeline job with one `train` step. Target: `make aml-pipeline-run`.

## Setup

1. Install the Azure CLI and its ML extension: `az extension add -n ml`.

2. Log in: `az login`.

3. Set the workspace. Put these lines in your shell profile, or add them to each `make` command:

    ```shell
    export AML_WORKSPACE=<workspace-name>
    export AML_RESOURCE_GROUP=<resource-group>
    ```

4. Check the setup: `make aml-login-check`.

## Run the training pipeline

```shell
make aml-check-definitions   # every YAML file under aml/ parses
make aml-compute-create      # once
make aml-env-create          # once, or after a change to aml/environments/env.yaml
make aml-pipeline-run        # uploads the code and submits the pipeline
```

`aml-pipeline-run` uses the component file directly, so you do not have to register the component first. Register it
with `make aml-component-create` when other pipelines or the Azure ML designer must use it.

## How a job runs

- The job uploads the repository root as the code snapshot. `.amlignore` excludes data, tests, docs and caches.
    When `.amlignore` exists, Azure ML ignores `.gitignore`, so keep large files out of both.
- The `config` input is a path in the code snapshot, for example `configs/train.yaml`. A config that is not committed
    (or is excluded by `.amlignore`) is not in the job.
- The command runs `uv run --frozen --no-dev`, which installs the dependencies from `uv.lock` when the job starts.
{%- if cookiecutter.docker == "yes" %}
- To put the dependencies in the image instead, use the commented `build:` block in `environments/env.yaml` and the
    commented command in `components/train.yaml`. The `Dockerfile` uses BuildKit features (`RUN --mount=type=cache`).
    The Azure ML image build may not support them. If it fails, build and push the image yourself and use `image:`.
{%- endif %}
- Azure ML sets `MLFLOW_TRACKING_URI` and `MLFLOW_EXPERIMENT_NAME` in the job. The project MLflow helpers
    (`{{cookiecutter.package_name}}.utils.mlflow.resolve_tracking_uri` and `resolve_experiment_name`) give these
    variables priority over the local settings. MLflow needs the `azureml-mlflow` package to log to an Azure ML
    workspace.
- Secrets do not go in these files. Use workspace connections or Azure Key Vault, and pass values to the job as
    environment variables (`environment_variables:` in the pipeline job).
