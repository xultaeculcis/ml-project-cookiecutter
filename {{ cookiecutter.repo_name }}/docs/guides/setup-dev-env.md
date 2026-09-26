# Setting up the dev environment

This page tells you how to create the local environment for this project.

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/). uv installs Python {{ cookiecutter.python_version }} (from
    `.python-version`) if it is not on your machine.
- `git`.
- `make`. On Windows, use WSL, or run the commands from the "Manual setup" section.
{%- if cookiecutter.docker == "yes" %}
- Docker, only for the `docker-*` targets.
{%- endif %}
{%- if cookiecutter.azure_ml == "yes" %}
- The Azure CLI with the `ml` extension, only for the `aml-*` targets.
{%- endif %}

## First setup of a new project

Run this command one time, after you generate the project from the template:

```shell
make init-project
```

The command does these steps:

1. It runs `make env`. This creates `.venv/` and `uv.lock` (if `uv.lock` does not exist), and installs all dependency
    groups.
2. It runs `make setup-pre-commit`. This installs the `pre-commit` git hooks.

Then commit `uv.lock`:

```shell
git add uv.lock
git commit -m "Add uv.lock"
```

## Setup of an existing clone

If the project already has a `uv.lock` file, use the same command:

```shell
make init-project
```

To update the environment later (for example after `git pull`), run:

```shell
make env
```

`make env` runs `uv sync --all-groups`. It installs the runtime dependencies and the `dev`, `docs` and `analysis`
groups. A plain `uv sync` or `uv run` installs only the runtime dependencies and the `dev` group.

## Manual setup

If you cannot use `make`, run these commands:

1. Create the environment:

    ```shell
    uv sync --all-groups
    ```

2. Install the `pre-commit` hooks:

    ```shell
    uv run pre-commit install
    ```
{%- if cookiecutter.ml_stack in ["torch", "lightning"] %}

## PyTorch wheels

On Linux, uv installs `torch` from the PyTorch CUDA 13.0 index (`pytorch-cu130` in `pyproject.toml`). These wheels
need an NVIDIA driver version 580 or newer. On macOS and Windows, uv installs the default wheels from PyPI.

To use a different CUDA version, change the index URL and name in `pyproject.toml`, then run `make lock`.
{%- endif %}

## Environment variables

The project reads settings from environment variables and from the `.env` file in the project root. Git ignores `.env`.
Do not commit secrets.

1. Copy the sample file:

    ```shell
    cp .env-sample .env
    ```

2. Set the values in `.env`. Ask the team for the values that are not in `.env-sample`.

Real environment variables have priority over the values in `.env`. Nested sections use `__` as the delimiter, for
example `MLFLOW__TRACKING_URI`. For more information, read [Experiment tracking](experiment-tracking.md).

## Pre-commit hooks

The `pre-commit` hooks run when you run `git commit`. They check and format the code, the Markdown files and the
config files. The `mypy` and `pytest-check` hooks use `uv run`, so they use the project environment and its
dependencies.

- To run all hooks on all files, run `make pc`.
- To run one hook, run `uv run pre-commit run <hook-id> --all-files`.
- To skip a hook one time, set `SKIP`, for example `SKIP=pytest-check git commit -m "..."`. Use this only when
    necessary.

## Dependencies

- To add a runtime dependency, run `uv add <package>`.
- To add a development dependency, run `uv add --dev <package>`.
- To add a dependency to a group, run `uv add --group <group> <package>`.
- After you edit `pyproject.toml` by hand, run `make lock`.
- To upgrade all locked dependencies, run `make upgrade`.

Commit `pyproject.toml` and `uv.lock` together.
