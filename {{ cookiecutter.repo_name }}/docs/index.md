# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Getting started

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).

2. Create the environment and install the `pre-commit` hooks:

    ```shell
    make init-project
    ```

3. Copy `.env-sample` to `.env` and set the values:

    ```shell
    cp .env-sample .env
    ```

4. Show all `make` targets:

    ```shell
    make help
    ```

For more information, read [Setting up the dev environment](guides/setup-dev-env.md).

## Project layout

- `configs/`: run configs (YAML). Pydantic models validate them.
- `data/`: local data. Git ignores the content. Only the `.gitkeep` files are committed.
- `docs/`: this documentation (MkDocs).
- `notebooks/`: Jupyter notebooks for exploration.
- `src/{{ cookiecutter.package_name }}/`: the Python package.
- `tests/`: the tests, in `unit/`, `integration/` and `e2e/`.

## Common tasks

- Run the CLI: `uv run {{ cookiecutter.repo_name }} --help`
- Run the fast tests: `make test`
- Run all `pre-commit` hooks: `make pc`
- Start the MLflow UI: `make mlflow-ui`
- Build the documentation: `make docs`
- Serve the documentation: `make docs-serve`

## Guides

- [Setting up the dev environment](guides/setup-dev-env.md)
- [Using Makefile commands](guides/makefile-usage.md)
- [Running tests](guides/tests.md)
- [Command-line interface](guides/cli.md)
- [Run configs](guides/configs.md)
- [Experiment tracking](guides/experiment-tracking.md)
- [CI and automation](guides/ci.md)
{%- if cookiecutter.azure_ml == "yes" %}
- [Azure ML](guides/azure-ml.md)
{%- endif %}
- [Contributing](guides/contributing.md)
