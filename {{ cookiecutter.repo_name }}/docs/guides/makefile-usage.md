In order to use the Makefile commands, you need to be on **Linux**.

## Basic usage

Makefile commands are easy to use. Just type `make` in your terminal, hit enter and see the list of available commands.

```shell
make
```

The command above is equivalent to running:

```shell
make help
```

## Development work commands

### Creating environments

- **env** - Creates env from the `pyproject.toml` file

    ```shell
    make env
    ```

- **setup-pre-commit** - Installs pre-commit hooks

    ```shell
    make setup-pre-commit
    ```

### Project initialization

- **init-project** - Runs project initialization - to be used after cookiecutter initialization

    ```shell
    make init-project
    ```

### Helper commands

- **format** - Runs code formatting (`ruff`)

    ```shell
    make format
    ```

- **type-check** - Runs type checking with `mypy`

    ```shell
    make type-check
    ```

- **test** - Runs pytest

    ```shell
    make test
    ```

- **testcov** - Runs tests and generates coverage reports

    ```shell
    make testcov
    ```

- **mpc** - Runs manual `pre-commit` stuff

    ```shell
    make mpc
    ```

- **docs** - Builds the documentation

    ```shell
    make docs
    ```

- **pc** - Runs `pre-commit` hooks

    ```shell
    make pc
    ```

- **clean** - Cleans artifacts

    ```shell
    make clean
    ```

### Docker commands

- **docker-all** - Docker default target - builds image and runs Docker container

    ```shell
    make docker-all
    ```

- **docker-build** - Build Docker image

    ```shell
    make docker-build
    ```

- **docker-run** - Run Docker container

    ```shell
    make docker-run
    ```

- **docker-stop** - Stop Docker container

    ```shell
    make docker-stop
    ```

- **docker-rm** - Remove Docker container

    ```shell
    make docker-rm
    ```

- **docker-rmi** - Remove Docker image

    ```shell
    make docker-rmi
    ```

- **docker-clean** - Clean up everything (container and image)

    ```shell
    make docker-clean
    ```

- **docker-rebuild** - Rebuild and rerun Docker container

    ```shell
    make docker-rebuild
    ```
