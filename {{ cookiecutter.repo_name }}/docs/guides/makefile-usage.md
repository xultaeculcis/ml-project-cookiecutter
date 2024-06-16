In order to use the Makefile commands you need to be on **Linux**.

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

### Git repo initialization

- **git-init** - Initializes Git repository

    ```shell
    make git-init
    ```

### Freezing project dependencies

- **lock-file** - Creates conda-lock file

    ```shell
    make lock-file
    ```

- **release-lock-file** - Creates conda-lock file without dev dependencies - to be used for deployment

    ```shell
    make release-lock-file
    ```

### Creating environments

- **conda-lock-install** - Creates env from conda-lock file

    ```shell
    make conda-lock-install
    ```

- **setup-pre-commit** - Installs pre-commit hooks

    ```shell
    make setup-pre-commit
    ```

- **setup-editable** - Installs the project in an editable mode

    ```shell
    make setup-editable
    ```

- **env** - Creates local environment and installs pre-commit hooks

    ```shell
    make env
    ```

### Project initialization

- **init-project** - Runs git init, lock-file creation and env setup - to be used after cookicutter initialization

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
