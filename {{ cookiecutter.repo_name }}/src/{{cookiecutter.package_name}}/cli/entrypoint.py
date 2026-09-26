"""CLI entrypoint.

Commands import their heavy dependencies inside the function body, so `--help` stays fast.

Examples:
    ```shell
    {{cookiecutter.repo_name}} --help
    {{cookiecutter.repo_name}} train --config configs/train.yaml
    {{cookiecutter.repo_name}} --log-level DEBUG evaluate --config configs/evaluate.yaml
{%- if cookiecutter.ml_stack == "lightning" %}
    {{cookiecutter.repo_name}} lightning fit --config configs/lightning/fit.yaml
{%- endif %}
    ```
"""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import contextlib
from pathlib import Path
from typing import TYPE_CHECKING

import click
from pydantic import ValidationError

from {{cookiecutter.package_name}}.core.configs import EvaluateConfig, PredictConfig, TrainConfig
from {{cookiecutter.package_name}}.utils.logging import configure_logging, get_logger

if TYPE_CHECKING:
    from collections.abc import Iterator

_logger = get_logger(__name__)
_LOG_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]

config_option = click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to the YAML config file.",
)


@contextlib.contextmanager
def _config_errors() -> Iterator[None]:
    """Show a config validation error as a CLI usage error, without a traceback."""
    try:
        yield
    except ValidationError as e:
        raise click.BadParameter(str(e), param_hint="--config") from e


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--log-level",
    type=click.Choice(_LOG_LEVELS, case_sensitive=False),
    default="INFO",
    show_default=True,
    help="Log level of the project loggers.",
)
def main(log_level: str) -> None:
    """Command-line interface of the {{cookiecutter.project_name}} project."""
    configure_logging(log_level)


@main.command()
@config_option
def train(config_path: Path) -> None:
    """Train a model."""
    from {{cookiecutter.package_name}}.utils.seed import seed_everything

    with _config_errors():
        config = TrainConfig.from_yaml(config_path)
    seed_everything(config.seed)
    _logger.info("Train config: %s", config.model_dump_json())
    _logger.info("TODO: implement training")


@main.command()
@config_option
def evaluate(config_path: Path) -> None:
    """Evaluate a trained model."""
    from {{cookiecutter.package_name}}.utils.seed import seed_everything

    with _config_errors():
        config = EvaluateConfig.from_yaml(config_path)
    seed_everything(config.seed)
    _logger.info("Evaluate config: %s", config.model_dump_json())
    _logger.info("TODO: implement evaluation")


@main.command()
@config_option
def predict(config_path: Path) -> None:
    """Make predictions with a trained model."""
    with _config_errors():
        config = PredictConfig.from_yaml(config_path)
    _logger.info("Predict config: %s", config.model_dump_json())
    _logger.info("TODO: implement prediction")
{%- if cookiecutter.ml_stack == "lightning" %}


@main.command(
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True, "help_option_names": []},
    add_help_option=False,
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def lightning(args: tuple[str, ...]) -> None:
    """Run LightningCLI. All arguments go to LightningCLI, e.g. `lightning fit --config configs/lightning/fit.yaml`."""
    import sys

    from {{cookiecutter.package_name}}.lightning.cli import run

    # LightningCLI reads `sys.argv`. Give it only its own arguments, so its help and error messages are correct.
    argv = sys.argv
    sys.argv = [f"{argv[0]} lightning", *args]
    try:
        run()
    finally:
        sys.argv = argv
{%- endif %}


if __name__ == "__main__":
    main()
