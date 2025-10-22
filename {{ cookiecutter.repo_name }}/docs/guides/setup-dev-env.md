## Requirements

To set up a local development environment, make sure you have installed:

- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Using Makefile

Run:

```shell
make env
```

It will also install `pre-commit` hooks and the project in an editable mode.

## Manually

1. Run `uv sync` command:

    ```shell
    uv sync --all-groups
    ```

## Pre-commit hooks

This project uses `pre-commit` package for managing and maintaining `pre-commit` hooks.

To ensure code quality - please make sure that you have it configured.

1. Install `pre-commit` and following packages: `ruff`, `mypy`, `pytest`.

2. Install `pre-commit` hooks by running: `pre-commit install`

3. The command above will automatically run formatters, code checks and other steps defined in the `.pre-commit-config.yaml`

4. All of those checks will also be run whenever a new commit is being created i.e., when you run `git commit -m "blah"`

5. You can also run it manually with this command: `pre-commit run --all-files`

You can manually disable `pre-commit` hooks by running: `pre-commit uninstall` Use this only in exceptional cases.

## Setup environmental variables

Ask your colleagues for `.env` files which aren't included in this repository and put them inside the repo's root directory.

To see what variables you need see the `.env-sample` file.
