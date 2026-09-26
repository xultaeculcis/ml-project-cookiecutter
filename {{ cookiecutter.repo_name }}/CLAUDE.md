# CLAUDE.md

Instructions for AI coding agents that work in this repository.

## Commands

- `make init-project`: create the environment (`uv sync --all-groups`) and install the `pre-commit` hooks.
- `make env`: update the environment after a dependency change.
- `make format`: fix lint issues and format the code (`ruff`).
- `make lint`: check lint and formatting without changes.
- `make type-check`: run `mypy` on `src` and `tests`.
- `make test`: run all tests except `slow` and `gpu`, in parallel.
- `make test-all`: run all tests.
- `make pc`: run all `pre-commit` hooks. Run it before you say that a change is complete.
- `make docs`: build the documentation.
- `uv run {{cookiecutter.repo_name}} --help`: run the project CLI.

## Layout

- `src/{{cookiecutter.package_name}}/cli/`: the click CLI (`train`, `evaluate`, `predict`{% if cookiecutter.ml_stack == "lightning" %}, `lightning`{% endif %}).
- `src/{{cookiecutter.package_name}}/core/settings.py`: settings from the environment and `.env` (pydantic-settings).
- `src/{{cookiecutter.package_name}}/core/configs.py`: pydantic models for the YAML run configs.
- `src/{{cookiecutter.package_name}}/consts/`: constants (directories, seed, MLflow defaults).
- `src/{{cookiecutter.package_name}}/utils/`: logging, MLflow, seed and serialization helpers.
{%- if cookiecutter.ml_stack == "lightning" %}
- `src/{{cookiecutter.package_name}}/lightning/`: LightningCLI runner, callbacks, example model and data module.
{%- endif %}
- `configs/`: YAML run configs. `configs/README.md` lists which model reads which file.
- `tests/unit/`, `tests/integration/`, `tests/e2e/`: the test suites.
- `docs/`: MkDocs documentation. The guides are in `docs/guides/`.
- `data/`, `notebooks/`: local data and exploration notebooks. Git ignores the content of `data/`.

## Conventions

- Use `uv` for all Python commands: `uv run ...`, `uv add ...`. Do not use `pip`.
- Line length is 120 characters. Write Google-style docstrings and type hints for all functions.
{%- if cookiecutter.python_version != "3.14" %}
- Each Python module starts with `from __future__ import annotations` (`ruff` adds it).
{%- endif %}
- Do not use `print()`. Use `{{cookiecutter.package_name}}.utils.logging.get_logger(__name__)`. Entry points call
    `configure_logging(level)` once.
- Put run parameters in `configs/*.yaml` and validate them with a model in `core/configs.py`. When you add a config
    family, add its loader to `CONFIG_LOADERS` in `tests/unit/test_configs.py`.
- Read secrets and machine-specific values only through `core.settings` (`get_settings()` or `settings`). Never
    commit `.env`.
- Tests get the `unit`, `integration` or `e2e` marker from their directory. Mark long tests `slow` and CUDA tests
    `gpu`. Unit tests cannot use the network.
- MLflow: the default tracking store is `sqlite:///mlflow.db`. A real `MLFLOW_TRACKING_URI` environment variable has
    priority. Use the helpers in `utils/mlflow.py`.
- Import heavy packages inside CLI command functions, so that `--help` stays fast.

## Documentation

- Guides: `docs/guides/`. Update the guide when you change a workflow, a `make` target or a CLI command.
- API reference: `docs/api_ref/` (mkdocstrings). Add a page or a section for a new module.
- Dev-logs: `docs/dev-logs/YYYY-MM-DD-<slug>/log.md`, registered in the `DEV-LOG` section of `mkdocs.yml`.

## Agent skills

- `CONTEXT.md`: read it first. It describes the problem, the data, the metric and how to run the project.
- `docs/glossary.md`: the project terms. Use these terms in code, docs and messages.
- `docs/adr/`: the architecture decision records. Read the related ADRs before you change a recorded decision.
    Write a new ADR for a decision that is hard to reverse.
- `docs/dev-logs/`: the experiment logs. Read `docs/dev-logs/log.md` for the format.
