"""Application settings.

Settings come from environment variables and from the `.env` file in the project root (`consts.directories.ROOT_DIR`).
Nested sections use `__` as the delimiter, for example `MLFLOW__TRACKING_URI`.

Nothing is read when this module is imported. `get_settings()` builds the `Settings` object on the first call and
caches it. The module-level `settings` object is a lazy proxy that calls `get_settings()` on the first attribute
access. A command that does not use settings therefore does not fail when the `.env` file or a variable is missing.

Examples:
    ```python
    import logging

    from {{cookiecutter.package_name}}.core.settings import get_settings, settings

    # Both give the same cached object.
    logging.info(settings.environment)  # INFO:local
    logging.info(get_settings().mlflow.tracking_uri)  # INFO:sqlite:///mlflow.db

    # An optional section: fail with a clear message only when the code needs it.
    storage = settings.storage.require("url", "access_key")
    ```

    Tests that change the environment must clear the cache: `get_settings.cache_clear()`.

"""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import functools
from typing import Any, ClassVar, Self, cast

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from {{cookiecutter.package_name}} import consts


class MissingSettingError(RuntimeError):
    """Raised when the code needs a setting that is not configured."""


class MLflowSettings(BaseModel):
    """MLflow tracking settings. Environment variables: `MLFLOW__TRACKING_URI`, `MLFLOW__EXPERIMENT_NAME`.

    Notes:
        MLflow itself reads `MLFLOW_TRACKING_URI` and `MLFLOW_EXPERIMENT_NAME` (single underscore). Azure ML sets these
        in its jobs. `{{cookiecutter.package_name}}.utils.mlflow.resolve_tracking_uri` and `resolve_experiment_name`
        give them priority over the values here.

    """

    tracking_uri: str = consts.tracking.DEFAULT_TRACKING_URI
    experiment_name: str | None = None


class StorageSettings(BaseModel):
    """Example of an optional section: credentials for a remote storage. Environment variables: `STORAGE__*`.

    All fields have defaults, so a missing section never stops the application from starting. The code that uses
    the storage calls `require()` with the fields it needs and gets a `MissingSettingError` that names the missing
    environment variables. Copy this pattern for each external service.

    """

    env_prefix: ClassVar[str] = "STORAGE"

    url: str | None = None
    access_key: SecretStr | None = None

    def require(self, *fields: str) -> Self:
        """Check that the fields are set and return this section.

        Args:
            *fields: The names of the fields the caller needs. If empty, all fields are required.

        Returns:
            This section.

        Raises:
            MissingSettingError: If one or more of the fields are not set or are empty.
            KeyError: If a field name is not a field of this section.

        """
        names = fields or tuple(type(self).model_fields)
        values = {name: getattr(self, name) for name in names if name in type(self).model_fields}
        unknown = set(names) - set(values)
        if unknown:
            raise KeyError(", ".join(sorted(unknown)))

        missing = [f"{self.env_prefix}__{name.upper()}" for name, value in values.items() if _is_empty(value)]
        if missing:
            msg = f"Missing settings. Set: {', '.join(missing)}."
            raise MissingSettingError(msg)
        return self


def _is_empty(value: Any) -> bool:
    if isinstance(value, SecretStr):
        value = value.get_secret_value()
    return value is None or not str(value).strip()


class Settings(BaseSettings):
    """Application settings with nested configuration sections."""

    environment: str = "local"
    mlflow: MLflowSettings = MLflowSettings()
    storage: StorageSettings = StorageSettings()

    model_config = SettingsConfigDict(
        env_file=consts.directories.ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


@functools.cache
def get_settings() -> Settings:
    """Build the application settings on the first call and return the cached object after that.

    Returns:
        The application settings.

    """
    return Settings()


class _LazySettings:
    """Proxy that builds the settings on the first attribute access."""

    def __getattr__(self, name: str) -> Any:
        return getattr(get_settings(), name)

    def __repr__(self) -> str:
        return f"<lazy {get_settings()!r}>"


settings: Settings = cast("Settings", _LazySettings())
