# Contributing

This page gives the coding style and the contribution rules for the team.

## Code

1. Use the `logging` module: `_logger = get_logger(__name__)` from `{{ cookiecutter.package_name }}.utils.logging`.
    Do not use `print()`. The `ruff` rule `T20` finds `print()` calls. Module loggers have no handler of their own.
    The CLI calls `configure_logging(level)` once, and `--log-level` then applies to all package loggers. Call
    `configure_logging` at the start of other entry points (scripts, notebooks) too.
2. Do not leave commented-out code. Use version control to keep old code.
3. If more than one module needs the same function, put it in a separate module and import it.
4. Use notebooks only for exploration. Production code goes in `src/{{ cookiecutter.package_name }}/`.
5. Set the line length guide in your IDE to 120 characters. The project uses 120 characters, not the 79 characters
    from PEP 8.
6. Add type hints to all functions. `mypy` checks them.
7. `ruff` checks and formats the code. Run `make format` before you commit.
8. Write docstrings in the Google style.
9. Use `uv` to manage dependencies. Do not use `pip install` in the project environment.

## Project structure

1. Add a new command to the CLI in `src/{{ cookiecutter.package_name }}/cli/entrypoint.py`. Read
    [Command-line interface](cli.md).
2. Put run parameters in a YAML file in `configs/` and validate them with a pydantic model. Read
    [Run configs](configs.md).
3. Put secrets and machine-specific values in `.env` and read them with
    `{{ cookiecutter.package_name }}.core.settings`. Do not put secrets in configs or code.
4. Log each training and evaluation run to MLflow. Read [Experiment tracking](experiment-tracking.md).
5. Write tests in the correct directory: `tests/unit/`, `tests/integration/` or `tests/e2e/`. Read
    [Running tests](tests.md).
6. Record experiment results in a dev-log entry. Read the [DEV-LOG intro](../dev-logs/log.md).
{%- if cookiecutter.agent_docs == "yes" %}
7. Record decisions that are hard to change in an ADR in `docs/adr/`. Read [About ADRs](../adr/README.md).
8. Define project terms in the [glossary](../glossary.md). Keep `CONTEXT.md` in the project root up to date.
{%- endif %}

## Git and pull requests

1. Do not push directly to the `main` branch.
2. Start each feature branch from the latest `main` branch.
3. Open a pull request for each change. Each pull request needs a code review.
4. Each pull request needs at least one approval, and all threads must be resolved before the merge.
5. All CI checks must pass before the merge.
6. Use "squash and merge" or "rebase and merge" to keep a linear history.
