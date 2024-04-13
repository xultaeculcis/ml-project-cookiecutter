from __future__ import annotations

from unittest.mock import MagicMock, patch

from {{cookiecutter.src_dir_name}}.core.configs.base import ConfigBase


class DummyConfig(ConfigBase):
    x: int
    y: float
    z: str


def test_config_base_str() -> None:
    cfg = DummyConfig(x=1, y=2.0, z="3")
    assert str(cfg) == '{\n    "x": 1,\n    "y": 2.0,\n    "z": "3"\n}'


@patch("{{cookiecutter.src_dir_name}}.core.configs.base._logger")
def test_config_base_log_self(mock_logger: MagicMock) -> None:
    cfg = DummyConfig(x=1, y=2.0, z="3")
    cfg.log_self()
    mock_logger.info.assert_called_once()
    args, kwargs = mock_logger.info.call_args
    assert "Running with following config" in args[0]
    assert kwargs["extra"]["cfg"] == cfg
