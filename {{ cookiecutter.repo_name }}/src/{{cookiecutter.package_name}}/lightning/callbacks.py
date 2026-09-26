"""Lightning callbacks."""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
from typing import TYPE_CHECKING

from lightning.pytorch.cli import SaveConfigCallback
from lightning.pytorch.loggers import MLFlowLogger

if TYPE_CHECKING:
    from lightning.pytorch import LightningModule, Trainer


class MLFlowSaveConfigCallback(SaveConfigCallback):
    """Save the full LightningCLI config as the `config.yaml` artifact of the MLflow run.

    Use it with `LightningCLI(save_config_callback=MLFlowSaveConfigCallback,
    save_config_kwargs={"save_to_log_dir": False})`. If the trainer does not use an `MLFlowLogger`, the callback
    does nothing.

    """

    def save_config(self, trainer: Trainer, pl_module: LightningModule, stage: str) -> None:  # noqa: ARG002
        """Log the config to the MLflow run of the trainer's logger.

        Args:
            trainer: The Trainer instance.
            pl_module: The LightningModule instance.
            stage: The current stage of the training.

        """
        logger = trainer.logger
        if not isinstance(logger, MLFlowLogger):
            return
        # skip_none=False keeps every key, so the file can reproduce the run.
        config = self.parser.dump(self.config, skip_none=False)
        logger.experiment.log_text(run_id=logger.run_id, text=config, artifact_file="config.yaml")
