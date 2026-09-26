{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
from unittest.mock import MagicMock

from lightning.pytorch.loggers import CSVLogger, MLFlowLogger

from {{cookiecutter.package_name}}.lightning.callbacks import MLFlowSaveConfigCallback


def _callback() -> MLFlowSaveConfigCallback:
    parser = MagicMock()
    parser.dump.return_value = "seed_everything: 42\n"
    return MLFlowSaveConfigCallback(parser=parser, config=MagicMock())


def test_logs_config_to_mlflow_run() -> None:
    logger = MagicMock(spec=MLFlowLogger)
    logger.run_id = "run-123"
    trainer = MagicMock(logger=logger)

    _callback().save_config(trainer, MagicMock(), stage="fit")

    logger.experiment.log_text.assert_called_once_with(
        run_id="run-123", text="seed_everything: 42\n", artifact_file="config.yaml"
    )


def test_does_nothing_without_mlflow_logger() -> None:
    logger = MagicMock(spec=CSVLogger)
    trainer = MagicMock(logger=logger)
    callback = _callback()

    callback.save_config(trainer, MagicMock(), stage="fit")

    callback.parser.dump.assert_not_called()
