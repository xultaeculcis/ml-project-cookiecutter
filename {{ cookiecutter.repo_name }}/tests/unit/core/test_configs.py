{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
from pathlib import Path

import pytest
from pydantic import ValidationError

from {{cookiecutter.package_name}} import consts
from {{cookiecutter.package_name}}.core.configs import PredictConfig, TrainConfig


def test_train_config_defaults() -> None:
    config = TrainConfig()
    assert config.seed == consts.reproducibility.SEED
    assert config.experiment_name is None
    assert config.data_dir == Path("data/processed")


def test_from_yaml(tmp_path: Path) -> None:
    path = tmp_path / "train.yaml"
    path.write_text("max_epochs: 3\ndata_dir: data/raw\n", encoding="utf-8")
    config = TrainConfig.from_yaml(path)
    assert config.max_epochs == 3
    assert config.data_dir == Path("data/raw")


def test_from_yaml_empty_file_gives_defaults(tmp_path: Path) -> None:
    path = tmp_path / "train.yaml"
    path.write_text("", encoding="utf-8")
    assert TrainConfig.from_yaml(path) == TrainConfig()


@pytest.mark.parametrize("content", ["unknown_key: 1\n", "max_epochs: 0\n", "learning_rate: -1\n"])
def test_from_yaml_rejects_invalid_content(tmp_path: Path, content: str) -> None:
    path = tmp_path / "train.yaml"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValidationError):
        TrainConfig.from_yaml(path)


def test_required_fields(tmp_path: Path) -> None:
    path = tmp_path / "predict.yaml"
    path.write_text("model_uri: models:/m/1\n", encoding="utf-8")
    with pytest.raises(ValidationError, match="input_path"):
        PredictConfig.from_yaml(path)


def test_to_dict_is_json_compatible() -> None:
    assert TrainConfig(data_dir=Path("data/raw")).to_dict()["data_dir"] == "data/raw"
