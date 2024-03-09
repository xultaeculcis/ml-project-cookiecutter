# ml-project-cookiecutter

A cookiecutter template for my private ML projects.

## Motivation

During my career I worked in a lot of different ML projects - computer vision, NLP, classical ML, time series
forecasting and others. The projects ranged from pure R&D, through PoCs and production ready stuff. Whenever I would
start a new project I found myself copying things from a bunch of different sources and my old projects again and
again - recreating and duplicating the work I did a dozen times before. Cookiecutter project templates to the resque!

The usage of technologies and certain patterns in the template is highly opinionated and is dictated by years
of experience of working with Data Scientists and R&D Engineers. As ML Engineer I would often find myself working
with low quality code, written by others in notebooks or scripts, without any form of documentation, standardized
coding style or even a way to reproduce the environment or analysis results. Moving that to production? Good luck!

In my opinion the fastest way to move ML stuff to production is **to force the Data Scientists** to write quality code
from the start. Want to add your changes to the repo? Sure, once all `pre-commit` hooks are green you'll be able to
commit your changes. Add to that a CI pipeline, automated tests and PR review process, and you'll have easier way to
ensure that the code and models are production ready faster.

Won't that slow down Data Scientists? Yes. At first at least. They'll have to learn working with a set of standard
python tools that are known in the industry for years. Spending a few hours on this is way better than spending
a few weeks on productionizing the code later. Your ML/MLOps Engineers will thank you for this.

???+ note
    Now, standardized code style, type hints and good documentation are just a small step to success. All of this doesn't
    mean much without code understanding and following good coding practices. In my opinion every great Data Scientist
    or ML Engineer should also be a great programmer. Learn how to write clean, testable code. Learn data structures,
    algorithms and design patterns. Have a CI in place. Verify changes via PRs and automated tests. Automate as much
    as you can. Integrate with other services that will allow you to ensure reproducibility, scaling, experiment tracing,
    artifact versioning and easier deployment.

This project was greatly inspired by
[Cookiecutter Data Science](https://github.com/drivendata/cookiecutter-data-science/) project.

## Features

- Integrated `pre-commit` hooks:
    - `pyupgrade`
    - `codespell`
    - `docformatter`
    - `ruff`
    - `mypy`
    - `pytest`
    - And a few more...
- Project documentation creation using [MkDocs](https://www.mkdocs.org/) with
    [Material](https://squidfunk.github.io/mkdocs-material/) theme.
- CI pipelines (Azure DevOps)
- Some useful utility classes and functions I found myself re-implementing again and again
- Folder structure inspired by [Cookiecutter Data Science](https://github.com/drivendata/cookiecutter-data-science/)
- Conda `env.yaml` file for reproducibility
- Makefile with a bunch of pre-defined commands
- Secrets support using `.env` files and [pydantic-settings](https://docs.pydantic.dev/latest/usage/pydantic_settings/)
- `pyproject.toml` with project tool configs

## Getting started

To get started, please check out [this](guide.md) guide.

## Contributing

Please refer to [this](contributing.md) guide.

## Running tests

To run the unit tests execute:

```shell
pytest tests
```
