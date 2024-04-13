from __future__ import annotations

from unittest.mock import patch

from {{cookiecutter.src_dir_name}}.core.settings import Settings, current_settings


def test_settings() -> None:
    assert current_settings is not None


@patch.dict("os.environ", {"ENVIRONMENT": "production"})
def test_environment_variable_override() -> None:
    settings = Settings()
    assert settings.environment == "production"
