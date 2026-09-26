# Using Makefile commands

The `Makefile` has shortcuts for the common tasks. Most targets run a tool with `uv run`. You need `make` and `bash`.
On Windows, use WSL, or run the commands from the target definitions in `Makefile` directly.

## Basic usage

To see all targets and their descriptions, run:

```shell
make
```

This is the same as `make help`. The help also lists the targets from the `mk/*.mk` files. The main `Makefile`
includes these files.

## Environment

- `make env`: create or update the local environment with all dependency groups (`uv sync --all-groups`). This
    creates `uv.lock` if it does not exist.
- `make setup-pre-commit`: install the `pre-commit` git hooks.
- `make init-project`: run `make env` and `make setup-pre-commit`. Use it one time after you generate the project or
    clone the repository.
- `make lock`: update `uv.lock` after you edit the dependencies in `pyproject.toml`.
- `make upgrade`: upgrade all locked dependencies to the latest allowed versions (`uv lock --upgrade`).

## Code quality

- `make format`: fix lint issues and format the code with `ruff`.
- `make lint`: check lint and formatting with `ruff`. This target does not change files.
- `make type-check`: run `mypy` on `src` and `tests`.
- `make pc`: run all `pre-commit` hooks on all files.

## Tests

- `make test`: run the tests in parallel (`pytest -n auto`). This target does not run tests marked `slow` or `gpu`.
- `make test-all`: run all tests in parallel, including the `slow` and `gpu` tests.
- `make testcov`: run the same tests as `make test` with coverage. It writes a terminal report, `htmlcov/` and
    `coverage.xml`. It fails if the coverage is below the threshold in `pyproject.toml`.

The test targets set `OMP_NUM_THREADS=1` and similar variables. Each `pytest-xdist` worker then uses one BLAS thread,
so the workers do not compete for the CPU cores. For more information, read [Running tests](tests.md).

## Documentation

- `make docs`: build the documentation into `docs-site/`.
- `make docs-serve`: serve the documentation at <http://127.0.0.1:8000> and rebuild it when files change.

## Experiment tracking

- `make mlflow-ui`: start the MLflow UI. It uses `MLFLOW_TRACKING_URI` from the shell. The default is
    `sqlite:///mlflow.db`.
- `make mlflow-gc`: permanently remove the MLflow runs and experiments that you deleted.

To use a different tracking store, set the variable, for example:

```shell
make mlflow-ui MLFLOW_TRACKING_URI=http://localhost:5000
```

## Analysis

- `make lab`: start JupyterLab with the `analysis` dependency group.

## Cleanup

- `make clean`: remove caches, coverage reports, build artifacts and `docs-site/`. It does not remove `.venv/`,
    `mlflow.db` or `data/`.
{%- if cookiecutter.docker == "yes" %}

## Docker (`mk/docker.mk`)

- `make docker-build`: build the Docker image.
- `make docker-run`: run the project CLI in a container. Give the CLI arguments with `ARGS`. Without `ARGS`, the
    container shows the CLI help.
- `make docker-shell`: start a `bash` shell in a container.
- `make docker-clean`: remove the Docker image.

If a `.env` file exists, `docker-run` and `docker-shell` give it to the container with `--env-file`.

Variables: `IMAGE_NAME` (default `{{ cookiecutter.repo_name }}`), `IMAGE_TAG` (default `latest`), `DOCKERFILE`,
`DOCKER_CONTEXT` and `ARGS`. Example:

```shell
make docker-build IMAGE_TAG=dev
make docker-run IMAGE_TAG=dev ARGS="train --config configs/train.yaml"
```
{%- endif %}
{%- if cookiecutter.azure_ml == "yes" %}

## Azure ML (`mk/aml.mk`)

These targets wrap `az ml` commands. They need the Azure CLI, the `ml` extension and an `az login` session. Set
`AML_WORKSPACE` and `AML_RESOURCE_GROUP` in the environment or on the command line.

- `make aml-login-check`: check the Azure login, the `ml` extension, `AML_WORKSPACE` and `AML_RESOURCE_GROUP`.
- `make aml-check-definitions`: check that each YAML file under `aml/` parses.
- `make aml-compute-create`: create or update the compute cluster (`AML_COMPUTE_FILE`).
- `make aml-env-create`: create a new version of the training environment (`AML_ENV_FILE`).
- `make aml-component-create`: register a new version of the training component (`AML_COMPONENT_FILE`).
- `make aml-pipeline-run`: submit the training pipeline (`AML_PIPELINE_FILE`). Give extra `az ml job create`
    arguments with `AML_JOB_ARGS`, for example `AML_JOB_ARGS="--stream"`.

Example:

```shell
make aml-pipeline-run AML_WORKSPACE=my-workspace AML_RESOURCE_GROUP=my-resource-group
```

For more information, read [Azure ML](azure-ml.md).
{%- endif %}

## Add a target

Add the target to `Makefile`, or to a new `mk/<topic>.mk` file. Write the help text on the `.PHONY` line, so that
`make help` shows it:

```makefile
.PHONY: my-target  ## Describe what the target does
my-target:
	uv run python -m {{ cookiecutter.package_name }} --help
```
