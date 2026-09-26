{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import os
from typing import TYPE_CHECKING

import pytest
from pydantic import SecretStr

from {{cookiecutter.package_name}} import consts
from {{cookiecutter.package_name}}.core.settings import (
    MissingSettingError,
    Settings,
    StorageSettings,
    get_settings,
    settings,
)

if TYPE_CHECKING:
    from pathlib import Path

_SETTINGS_ENV_PREFIXES = ("ENVIRONMENT", "MLFLOW__", "STORAGE__")


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in list(os.environ):
        if key.startswith(_SETTINGS_ENV_PREFIXES):
            monkeypatch.delenv(key)


def test_defaults() -> None:
    s = Settings(_env_file=None)
    assert s.environment == "local"
    assert s.mlflow.tracking_uri == consts.tracking.DEFAULT_TRACKING_URI == "sqlite:///mlflow.db"
    assert s.mlflow.experiment_name is None
    assert s.storage.url is None
    assert s.storage.access_key is None


def test_env_var_overrides_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "production")
    assert Settings(_env_file=None).environment == "production"


def test_nested_env_var_overrides_section_field(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MLFLOW__TRACKING_URI", "http://mlflow.example:5000")
    monkeypatch.setenv("MLFLOW__EXPERIMENT_NAME", "my-experiment")
    s = Settings(_env_file=None)
    assert s.mlflow.tracking_uri == "http://mlflow.example:5000"
    assert s.mlflow.experiment_name == "my-experiment"


def test_env_file_is_read_and_env_var_wins(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("ENVIRONMENT=from-file\nSTORAGE__URL=https://storage.example\n", encoding="utf-8")
    monkeypatch.setenv("ENVIRONMENT", "from-env")
    s = Settings(_env_file=env_file)
    assert s.environment == "from-env"
    assert s.storage.url == "https://storage.example"


def test_require_raises_with_missing_env_var_names() -> None:
    with pytest.raises(MissingSettingError, match=r"STORAGE__URL, STORAGE__ACCESS_KEY"):
        StorageSettings().require()


def test_require_checks_only_named_fields() -> None:
    section = StorageSettings(url="https://storage.example")
    assert section.require("url") is section
    with pytest.raises(MissingSettingError, match="STORAGE__ACCESS_KEY") as exc_info:
        section.require("url", "access_key")
    assert "STORAGE__URL" not in str(exc_info.value)


def test_require_treats_blank_values_as_missing() -> None:
    section = StorageSettings(url="  ", access_key=SecretStr(""))
    with pytest.raises(MissingSettingError, match=r"STORAGE__URL, STORAGE__ACCESS_KEY"):
        section.require()


def test_require_passes_when_all_fields_are_set() -> None:
    section = StorageSettings(url="https://storage.example", access_key=SecretStr("secret"))
    assert section.require() is section


def test_require_rejects_unknown_field_names() -> None:
    with pytest.raises(KeyError, match="no_such_field"):
        StorageSettings().require("no_such_field")


def test_get_settings_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "first")
    first = get_settings()
    monkeypatch.setenv("ENVIRONMENT", "second")
    assert get_settings() is first
    assert get_settings().environment == "first"

    get_settings.cache_clear()
    assert get_settings().environment == "second"


def test_lazy_proxy_builds_settings_on_first_access(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "lazy")
    assert get_settings.cache_info().currsize == 0
    assert settings.environment == "lazy"
    assert get_settings.cache_info().currsize == 1
    assert settings.mlflow is get_settings().mlflow
