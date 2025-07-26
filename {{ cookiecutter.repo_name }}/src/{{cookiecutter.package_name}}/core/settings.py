"""Application settings.

Examples:
    ```python
    import logging

    from src.core.settings import current_settings


    # log current environment
    logging.info(current_settings.env)  # INFO:dev
    ```

"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

from {{cookiecutter.package_name}} import consts


class Settings(BaseSettings):
    """Represents Application Settings with nested configuration sections."""

    environment: str = "local"

    model_config = SettingsConfigDict(
        env_file=consts.directories.ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


def current_settings() -> Settings:
    """Instantiate current application settings.

    Returns:
        Current application settings.

    """
    return Settings()
