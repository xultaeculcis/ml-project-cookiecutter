# ml-project-cookiecutter

![license](https://img.shields.io/github/license/xultaeculcis/ml-project-cookiecutter)
[![codecov](https://codecov.io/gh/xultaeculcis/ml-project-cookiecutter/branch/main/graph/badge.svg?token=2CBERR0ACO)](https://codecov.io/gh/xultaeculcis/ml-project-cookiecutter)
[![project-creation-checks](https://github.com/xultaeculcis/ml-project-cookiecutter/actions/workflows/project-creation-checks.yaml/badge.svg)](https://github.com/xultaeculcis/ml-project-cookiecutter/actions/workflows/project-creation-checks.yaml)
[![pr](https://github.com/xultaeculcis/ml-project-cookiecutter/actions/workflows/pr.yaml/badge.svg)](https://github.com/xultaeculcis/ml-project-cookiecutter/actions/workflows/pr.yaml)
[![zizmor](https://github.com/xultaeculcis/ml-project-cookiecutter/actions/workflows/zizmor-sec-check.yaml/badge.svg)](https://github.com/xultaeculcis/ml-project-cookiecutter/actions/workflows/zizmor-sec-check.yaml)
[![docs](https://github.com/xultaeculcis/ml-project-cookiecutter/actions/workflows/docs.yaml/badge.svg)](https://github.com/xultaeculcis/ml-project-cookiecutter/actions/workflows/docs.yaml)

A cookiecutter template for my private ML projects.

## Motivation

During my career I worked in a lot of different ML projects - computer vision, NLP, classical ML, time series
forecasting and others. The projects ranged from pure R&D, through PoCs and production ready stuff. Whenever I would
start a new project, I found myself copying things from a bunch of different sources and my old projects again and
again - recreating and duplicating the work I did a dozen times before. Cookiecutter project templates to the rescue!

The usage of technologies and certain patterns in the template is highly opinionated and is dictated by years
of experience of working with Data Scientists and R&D Engineers. As an ML Engineer, I would often find myself working
with low quality code, written by others in notebooks or scripts, without any form of documentation, standardized
coding style or even a way to reproduce the environment or analysis results. Moving that to production? Good luck!

In my opinion, the fastest way to move ML stuff to production is **to force the Data Scientists** to write quality code
from the start. Want to add your changes to the repo? Sure, once all `pre-commit` hooks are green you'll be able to
commit your changes. Add to that a CI pipeline, automated tests and PR review process, and you'll have an easier way to
ensure that the code and models are production ready faster.

Won't that slow down Data Scientists? Yes. At first at least. They'll have to learn working with a set of standard
python tools that are known in the industry for years. Spending a few hours on this is way better than spending
a few weeks on productionizing the code later. Your ML/MLOps Engineers will thank you for this.

> [!IMPORTANT]
> Now, standardized code style, type hints and good documentation are just a small step to success. All of this doesn't
> mean much without code understanding and following good coding practices. In my opinion every great Data Scientist
> or ML Engineer should also be a great programmer. Learn how to write clean, testable code. Learn data structures,
> algorithms and design patterns. Have a CI in place. Verify changes via PRs and automated tests. Automate as much
> as you can. Integrate with other services that will allow you to ensure reproducibility, scaling, experiment tracing,
> artifact versioning and easier deployment.

This project was greatly inspired by
[Cookiecutter Data Science](https://github.com/drivendata/cookiecutter-data-science/) project.

## Features

- Options for the ML stack (scikit-learn, PyTorch, PyTorch Lightning or none), the CI provider (GitHub Actions, Azure
    Pipelines or none), Dependabot, a monthly lock file update workflow, `zizmor` checks, Docker, Azure ML and agent
    docs. The files of options that you do not select are not in the project.
- Python 3.11 to 3.14. [uv](https://docs.astral.sh/uv/) manages the environment, with a committed `uv.lock` and
    `.python-version`.
- `pre-commit` hooks: `pre-commit-hooks`, `codespell`, `ruff` (lint and format), `mdformat`, `uv-lock`, `zizmor`,
    `mypy` and `pytest`. The `mypy` and `pytest` hooks run in the project environment with `uv run`.
- A [click](https://click.palletsprojects.com/) CLI with `train`, `evaluate` and `predict` commands, and a
    LightningCLI command for the Lightning stack.
- YAML run configs in `configs/`, validated by pydantic models. A test loads every committed config.
- Lazy settings from environment variables and `.env` files with
    [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).
- [MLflow](https://mlflow.org/) experiment tracking with a local SQLite store, helper functions and `make mlflow-ui`.
- `pytest` with `unit`, `integration` and `e2e` markers from the test directory, `slow` and `gpu` markers,
    `pytest-socket` for unit tests, `pytest-xdist` and a coverage threshold.
- Documentation with [MkDocs](https://www.mkdocs.org/) and the
    [Material](https://squidfunk.github.io/mkdocs-material/) theme: guides, an API reference (mkdocstrings) and
    dev-logs for experiment results.
- A `Makefile` with targets for the environment, code quality, tests, docs, MLflow, Docker and Azure ML.
- A multi-stage `Dockerfile` that runs as a non-root user.
- Agent docs: `CLAUDE.md`, `CONTEXT.md`, a glossary and architecture decision records.
- Folder structure inspired by [Cookiecutter Data Science](https://github.com/drivendata/cookiecutter-data-science/).
- Template updates for existing projects with [cruft](https://cruft.github.io/cruft/).

## Getting started

Install [uv](https://docs.astral.sh/uv/getting-started/installation/). Then create a project:

```shell
uvx cookiecutter gh:xultaeculcis/ml-project-cookiecutter
```

Go to the new project directory and run:

```shell
make init-project
```

This creates the environment and `uv.lock`, and installs the `pre-commit` hooks.

To get template updates later, create the project with [cruft](https://cruft.github.io/cruft/) instead:

```shell
uvx cruft create https://github.com/xultaeculcis/ml-project-cookiecutter
```

For the full guide (all options, the generated files, CI setup and template updates), see
[this](https://xultaeculcis.github.io/ml-project-cookiecutter/guide/) page.

## Contributing

Please refer to [this](https://xultaeculcis.github.io/ml-project-cookiecutter/contributing/) guide.

## Running tests

To run the fast tests, execute:

```shell
make test
```

To run all tests, including the slow tests that run the tooling of generated projects, execute:

```shell
make test-all
```
