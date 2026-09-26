# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

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

4. Run the CLI:

    ```shell
    uv run {{cookiecutter.repo_name}} --help
    ```

To see all `make` targets, run `make help`.

## Common commands

- `make test`: run the fast tests.
- `make pc`: run all `pre-commit` hooks.
- `make mlflow-ui`: start the MLflow UI for the local tracking store (`mlflow.db`).
- `make docs-serve`: serve the documentation at <http://127.0.0.1:8000>.

## Guides

- [Setting up the dev environment](docs/guides/setup-dev-env.md)
- [Using Makefile commands](docs/guides/makefile-usage.md)
- [Running tests](docs/guides/tests.md)
- [Command-line interface](docs/guides/cli.md)
- [Run configs](docs/guides/configs.md)
- [Experiment tracking](docs/guides/experiment-tracking.md)
- [CI and automation](docs/guides/ci.md)
{%- if cookiecutter.azure_ml == "yes" %}
- [Azure ML](docs/guides/azure-ml.md)
{%- endif %}
- [Contributing](docs/guides/contributing.md)

## Dev-logs

The [dev-logs](docs/dev-logs/log.md) record the experiments and their results. To read them, run `make docs-serve`.
{%- if cookiecutter.agent_docs == "yes" %}

## Project knowledge

- [CONTEXT.md](CONTEXT.md): the problem, the data, the metric and how to run the project.
- [Glossary](docs/glossary.md): the project terms.
- [Architecture decision records](docs/adr/README.md): the decisions that are hard to change.
- [CLAUDE.md](CLAUDE.md): instructions for AI coding agents.
{%- endif %}
