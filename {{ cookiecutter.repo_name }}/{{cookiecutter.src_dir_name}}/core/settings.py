from __future__ import annotations

from pydantic_settings import BaseSettings

from {{cookiecutter.src_dir_name}} import consts


class Settings(BaseSettings):
    """Represents Application Settings with nested configuration sections"""

    environment: str = "local"

    class Config:
        env_file = consts.directories.ROOT_DIR / ".env"
        env_file_encoding = "utf-8"


current_settings = Settings()
