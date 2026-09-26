# Azure ML

The `aml/` directory has the definitions to run the project CLI as Azure ML jobs. The `make aml-*` targets in
`mk/aml.mk` run the `az ml` commands. `aml/README.md` has the same information in short form.

## Files

- `aml/environments/env.yaml`: the job environment. It is a Python image with uv.{% if cookiecutter.docker == "yes" %} A
    commented alternative builds the environment from the project `Dockerfile`.{% endif %} Target:
    `make aml-env-create`.
- `aml/compute/cpu-cluster.yaml`: a CPU cluster that scales to zero nodes when it has no jobs. Target:
    `make aml-compute-create`.
- `aml/components/train.yaml`: a command component that runs
    `{{ cookiecutter.repo_name }} train --config <config>`. Target: `make aml-component-create`.
- `aml/pipelines/train-pipeline.yaml`: a pipeline job with one `train` step. Target: `make aml-pipeline-run`.
- `.amlignore`: the files that Azure ML does not upload with the code.

## Setup

1. Install the Azure CLI.

2. Install the `ml` extension:

    ```shell
    az extension add -n ml
    ```

3. Log in:

    ```shell
    az login
    ```

4. Set the workspace and the resource group. Put these lines in your shell profile, or add them to each `make`
    command:

    ```shell
    export AML_WORKSPACE=<workspace-name>
    export AML_RESOURCE_GROUP=<resource-group>
    ```

5. Check the setup:

    ```shell
    make aml-login-check
    ```

## Run the training pipeline

```shell
make aml-check-definitions   # check that each YAML file under aml/ parses
make aml-compute-create      # one time
make aml-env-create          # after each dependency change
make aml-pipeline-run        # upload the code and submit the pipeline
```

`aml-pipeline-run` uses the component file directly, so you do not have to register the component first. Register it
with `make aml-component-create` when other pipelines or the Azure ML designer must use it.

To see the job logs in the terminal, add `AML_JOB_ARGS="--stream"`.

## How a job runs

- The job uploads the repository root as the code snapshot. `.amlignore` excludes data, tests, docs and caches. When
    `.amlignore` exists, Azure ML ignores `.gitignore`. Keep large files out of both files.
- The `config` input is a path in the code snapshot, for example `configs/train.yaml`. A config that is not in the
    snapshot is not available to the job.
- The command runs `uv run --frozen --no-dev`. This installs the dependencies from `uv.lock` when the job starts.
{%- if cookiecutter.docker == "yes" %}
- To put the dependencies in the image instead, use the commented `build:` block in `aml/environments/env.yaml` and
    the commented command in `aml/components/train.yaml`. That command sets `PYTHONPATH=src`, so the job runs the
    uploaded source code with the dependencies from the image. Run `make aml-env-create` after a change to
    `pyproject.toml`, `uv.lock` or `Dockerfile`.
- The `Dockerfile` uses BuildKit features (`# syntax=` and `RUN --mount=type=cache`). The Azure ML image build in
    the workspace container registry may not support them. If the build fails, build and push the image yourself
    (`make docker-build`, then `docker push`) and set `image: <registry>.azurecr.io/<name>:<tag>` in
    `aml/environments/env.yaml`.
{%- endif %}
- Azure ML sets `MLFLOW_TRACKING_URI` and `MLFLOW_EXPERIMENT_NAME` in the job. The experiment name comes from
    `experiment_name` in the pipeline file. The MLflow helpers of the project give these variables priority over the
    local settings. The `azureml-mlflow` runtime dependency lets MLflow log to the workspace. Read
    [Experiment tracking](experiment-tracking.md).

## Secrets

Do not put secrets in the `aml/` files. Use workspace connections or Azure Key Vault. Give values to the job as
environment variables (`environment_variables:` in the pipeline job).

## Change the definitions

- To use a GPU cluster, add a compute file (for example `aml/compute/gpu-cluster.yaml`) and change
    `default_compute` in the pipeline file.
- To use a different config, change the `config` input in `aml/pipelines/train-pipeline.yaml`.
- To use other files, set the variables, for example `make aml-pipeline-run AML_PIPELINE_FILE=aml/pipelines/other.yaml`.
