from __future__ import annotations

from pydantic import BaseModel

from {{cookiecutter.src_dir_name}}.utils.logging import get_logger

_logger = get_logger("config")


class ConfigBase(BaseModel):
    """A base class for all entrypoint config classes."""

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)  # type: ignore[no-any-return]

    def log_self(self) -> None:
        """Logs a short info with INFO logging level about what parameters is the script being run with."""
        _logger.info("Running with following config: $(cfg)", extra={"cfg": self})
