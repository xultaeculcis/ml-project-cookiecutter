# Running tests

This page tells you how the tests are organized and how to run them with `pytest`.

## Test suites and markers

The tests are in three directories. `tests/conftest.py` adds a marker to each test from the name of its directory. You
do not add these markers by hand.

- `tests/unit/` gets the `unit` marker. Unit tests are fast and isolated. They cannot use the network: `pytest-socket`
    blocks all sockets except Unix sockets.
- `tests/integration/` gets the `integration` marker. Integration tests can use real files, I/O and services. The
    example tests run the CLI with `click.testing.CliRunner`.
- `tests/e2e/` gets the `e2e` marker. End-to-end tests run a full workflow. The example tests run
    `python -m {{ cookiecutter.package_name }}` in a subprocess.

Add these markers by hand when they apply:

- `slow`: a long-running test. `make test` does not run it.
- `gpu`: a test that needs a CUDA device. `make test` does not run it.

```python
import pytest


@pytest.mark.slow
def test_full_training_run() -> None: ...
```

`pytest` runs with `--strict-markers`. A marker that is not registered in `pyproject.toml` is an error.

## Run the tests

- `make test`: all tests except `slow` and `gpu`, in parallel with `pytest-xdist`.
- `make test-all`: all tests, in parallel.
- `make testcov`: the same tests as `make test`, with a coverage report. The run fails if the coverage is below the
    `fail_under` value in `pyproject.toml`.

To select tests by marker, use `-m`:

```shell
uv run pytest -m unit
uv run pytest -m "integration or e2e"
uv run pytest -m "not slow and not gpu"
```

To run one file or one test, give its path:

```shell
uv run pytest tests/unit/utils/test_seed.py
uv run pytest tests/unit/utils/test_seed.py::test_default_seed
```

## What the pre-commit hook runs

The `pytest-check` hook runs on each commit:

```shell
uv run pytest -m "unit and not slow" -q -p no:cacheprovider
```

It runs only the fast unit tests. Run `make test` before you open a pull request.

## Tests and settings

`tests/conftest.py` clears the settings cache (`get_settings.cache_clear()`) before each test. A test can change
the environment with `monkeypatch.setenv` and then call `get_settings()` to get new settings.

MLflow telemetry is turned off in the tests (`MLFLOW_DISABLE_TELEMETRY=true`), because unit tests cannot use the
network. Tests that write MLflow runs must use a temporary tracking URI, for example
`sqlite:///<tmp_path>/mlflow.db`. Do not write to the project `mlflow.db` from tests.
