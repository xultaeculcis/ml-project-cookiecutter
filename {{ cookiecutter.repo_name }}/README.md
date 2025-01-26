# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

## Getting started

Create the environment:

```shell
make env
```

Run `pre-commit` hooks:

```shell
make pc
```

## Dev LOG

See the [log](docs/dev-logs) of changes and experiment results. Best to view it via `mkdocs serve` command.

## Guides

Read more here:

- [Development env setup](docs/guides/setup-dev-env.md)
- [Contributing](docs/guides/contributing.md)
- [Makefile usage](docs/guides/makefile-usage.md)
- [Running tests](docs/guides/tests.md)

## Docs

To build project documentation run:

```shell
make docs
```

and then:

```shell
mkdocs serve
```
