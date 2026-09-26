# Command-line interface

The project has one command-line interface (CLI), built with [click](https://click.palletsprojects.com/). The console
script is `{{ cookiecutter.repo_name }}`. It is defined in `pyproject.toml` (`[project.scripts]`) and points to
`{{ cookiecutter.package_name }}.cli.entrypoint:main`.

## Run the CLI

Use one of these commands:

```shell
uv run {{ cookiecutter.repo_name }} --help
uv run python -m {{ cookiecutter.package_name }} --help
```

The `--log-level` option sets the log level (`CRITICAL`, `ERROR`, `WARNING`, `INFO` or `DEBUG`). The default is
`INFO`. Put the option before the command name:

```shell
uv run {{ cookiecutter.repo_name }} --log-level DEBUG train --config configs/train.yaml
```

## Commands

Each command reads one YAML config with `--config PATH` and validates it with a pydantic model. An invalid config
stops the command with a usage error. For more information, read [Run configs](configs.md).

- `train --config configs/train.yaml`: train a model. Reads `TrainConfig` and calls `seed_everything(config.seed)`.
- `evaluate --config configs/evaluate.yaml`: evaluate a trained model. Reads `EvaluateConfig` and calls
    `seed_everything(config.seed)`.
- `predict --config configs/predict.yaml`: make predictions with a trained model. Reads `PredictConfig`.
{%- if cookiecutter.ml_stack == "lightning" %}
- `lightning ARGS...`: run [LightningCLI](https://lightning.ai/docs/pytorch/stable/cli/lightning_cli.html). The
    command gives all arguments to LightningCLI.
{%- endif %}

The `train`, `evaluate` and `predict` commands are stubs. They load and log the config, and then log a `TODO`
message. Put your code in the command functions, or call your own modules from them.
{%- if cookiecutter.ml_stack == "lightning" %}

## LightningCLI

The `lightning` command runs `{{ cookiecutter.package_name }}.lightning.cli.run`. The config selects the model and the
data module with `class_path`. The trainer logs to MLflow.

```shell
# Train the example model with the example config.
uv run {{ cookiecutter.repo_name }} lightning fit --config configs/lightning/fit.yaml

# Override one value from the command line.
uv run {{ cookiecutter.repo_name }} lightning fit --config configs/lightning/fit.yaml --trainer.max_epochs 5

# Show all options with their default values.
uv run {{ cookiecutter.repo_name }} lightning fit --print_config

# Show the LightningCLI help.
uv run {{ cookiecutter.repo_name }} lightning --help
```

The `MLFlowSaveConfigCallback` callback saves the full config as the `config.yaml` artifact of the MLflow run. Use
this artifact to repeat a run.

The example model (`LinearRegressionModule`) and data module (`RandomRegressionDataModule`) are in
`src/{{ cookiecutter.package_name }}/lightning/`. Replace them with your model and data, and change
`configs/lightning/fit.yaml`.
{%- endif %}

## Add a command

1. Add a function to `src/{{ cookiecutter.package_name }}/cli/entrypoint.py` and decorate it with `@main.command()`.

2. Add the `@config_option` decorator if the command reads a config.

3. Import heavy packages (for example `torch` or `sklearn`) inside the function body. Then `--help` stays fast.

    ```python
    @main.command()
    @config_option
    def export(config_path: Path) -> None:
        """Export a trained model."""
        from {{ cookiecutter.package_name }}.export import export_model

        export_model(config_path)
    ```

4. Add a test to `tests/unit/cli/` or `tests/integration/test_cli.py`.
{%- if cookiecutter.docker == "yes" %}

## Run the CLI in Docker

The Docker image runs the CLI. The default command shows the help.

```shell
make docker-build
make docker-run ARGS="train --config configs/train.yaml"
```
{%- endif %}
