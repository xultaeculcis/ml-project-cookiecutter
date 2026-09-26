"""LightningCLI runner.

`{{cookiecutter.repo_name}} lightning <subcommand> ...` calls `run` with all arguments. The model and the data module
are selected in the config with `class_path`, see `configs/lightning/fit.yaml`.

The trainer logs to MLflow. The tracking URI and the experiment name come from `MLFLOW_TRACKING_URI` and
`MLFLOW_EXPERIMENT_NAME` if set (Azure ML sets them), otherwise from the settings (`MLFLOW__TRACKING_URI`,
`MLFLOW__EXPERIMENT_NAME`). A config can override any of this under `trainer.logger`.

Examples:
    ```shell
    {{cookiecutter.repo_name}} lightning fit --config configs/lightning/fit.yaml
    {{cookiecutter.repo_name}} lightning fit --config configs/lightning/fit.yaml --trainer.max_epochs 5
    {{cookiecutter.repo_name}} lightning fit --print_config
    ```
"""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
from typing import TYPE_CHECKING

from lightning.pytorch import LightningDataModule, LightningModule
from lightning.pytorch.cli import LightningCLI

from {{cookiecutter.package_name}} import consts
from {{cookiecutter.package_name}}.core.settings import get_settings
from {{cookiecutter.package_name}}.lightning.callbacks import MLFlowSaveConfigCallback
from {{cookiecutter.package_name}}.utils.mlflow import resolve_experiment_name, resolve_tracking_uri, run_id_from_context

if TYPE_CHECKING:
    from lightning.pytorch.cli import ArgsType


def run(args: ArgsType = None, *, run_subcommand: bool = True) -> LightningCLI:
    """Run LightningCLI.

    Args:
        args: The command-line arguments, for example `["fit", "--config", "configs/lightning/fit.yaml"]`.
            If `None`, LightningCLI reads `sys.argv`.
        run_subcommand: If `False`, only parse the config and create the objects. Then `args` has no subcommand,
            for example `["--config", "configs/lightning/fit.yaml"]`.

    Returns:
        The LightningCLI instance, with the trainer, the model and the data module.

    """
    mlflow_settings = get_settings().mlflow
    return LightningCLI(
        model_class=LightningModule,
        datamodule_class=LightningDataModule,
        subclass_mode_model=True,
        subclass_mode_data=True,
        save_config_callback=MLFlowSaveConfigCallback,
        save_config_kwargs={"save_to_log_dir": False},
        trainer_defaults={
            "default_root_dir": "outputs/lightning",
            "logger": {
                "class_path": "lightning.pytorch.loggers.MLFlowLogger",
                "init_args": {
                    "experiment_name": resolve_experiment_name(
                        mlflow_settings.experiment_name or consts.tracking.DEFAULT_EXPERIMENT_NAME
                    ),
                    "tracking_uri": resolve_tracking_uri(mlflow_settings.tracking_uri),
                    "run_id": run_id_from_context(),
                },
            },
        },
        seed_everything_default=consts.reproducibility.SEED,
        args=args,
        run=run_subcommand,
    )
