import json

from pydantic import BaseModel

from {{cookiecutter.src_dir_name}}.utils.logging import get_logger
from {{cookiecutter.src_dir_name}}.utils.serialization import JsonEncoder

_logger = get_logger("config")


class ConfigBase(BaseModel):
    """A base class for all entrypoint config classes."""

    def __str__(self) -> str:
        return json.dumps(self.model_dump(), cls=JsonEncoder, indent=4)

    def log_self(self) -> None:
        """Logs a short info with INFO logging level about what parameters is
        the script being run with."""
        _logger.info(f"Running with following config: {self}")
