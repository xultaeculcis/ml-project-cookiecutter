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

### Freezing project dependencies

* **conda-lock-win-64** - Creates conda-lock file for `win-64` platform

    ```shell
    make conda-lock-win-64
    ```

* **conda-lock-linux-64** - Creates conda-lock file for `linux-64` platform

    ```shell
    make conda-lock-linux-64
    ```

* **conda-lock-osx-arm64** - Creates conda-lock file for `osx-arm64` platform

    ```shell
    make conda-lock-osx-arm64
    ```

* **conda-lock-all-platforms** - Creates conda-lock file for `win-64`, `linux-64` and `osx-arm64` platforms

    ```shell
    make conda-lock-all-platforms
    ```

### Creating environments

* **conda-install-win-64** - Creates env from conda-lock file for `win-64` platform

    ```shell
    make conda-install-win-64
    ```

* **conda-install-linux-64** - Creates env from conda-lock file for `linux-64` platform

    ```shell
    make conda-install-linux-64
    ```

* **conda-install-osx-arm64** - Creates env from conda-lock file for `osx-arm64` platform

    ```shell
    make conda-install-osx-arm64
    ```

* **setup-pre-commit** - Installs pre-commit hooks

    ```shell
    make setup-pre-commit
    ```

* **setup-editable** - Installs the project in an editable mode

    ```shell
    make setup-editable
    ```

* **setup-local-env-win-64** - Creates local environment and installs pre-commit hooks for `win-64` platform

    ```shell
    make setup-local-env-win-64
    ```

* **setup-local-env-linux-64** - Creates local environment and installs pre-commit hooks for `linux-64` platform

    ```shell
    make setup-local-env-linux-64
    ```

* **setup-local-env-osx-arm64** - Creates local environment and installs pre-commit hooks for `osx-arm64` platform

    ```shell
    make setup-local-env-osx-arm64
    ```

### Helper commands

* **format** - Runs code formatting (`isort`, `black`, `flake8`)

    ```shell
    make format
    ```

* **type-check** - Runs type checking with `mypy`

    ```shell
    make type-check
    ```

* **test** - Runs pytest

    ```shell
    make test
    ```

* **testcov** - Runs tests and generates coverage reports

    ```shell
    make testcov
    ```

* **mpc** - Runs manual `pre-commit` stuff

    ```shell
    make mpc
    ```

* **docs** - Builds the documentation

    ```shell
    make docs
    ```

* **pc** - Runs `pre-commit` hooks

    ```shell
    make pc
    ```

* **clean** - Cleans artifacts

    ```shell
    make clean
    ```
