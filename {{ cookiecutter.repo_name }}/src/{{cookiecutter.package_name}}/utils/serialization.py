"""Serialization utils."""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
from datetime import date, datetime, time
from enum import Enum
from json import JSONEncoder
from pathlib import Path
from typing import Any
from uuid import UUID

import numpy as np


class JsonEncoder(JSONEncoder):
    """JSON encoder for types that the `json` package does not support.

    Supported types: `date`, `datetime`, `time`, `Path`, `Enum`, `UUID`, `set`, `frozenset`, numpy scalars and numpy
    arrays.

    Examples:
        >>> import json
        >>> json.dumps({"n": np.int64(3), "tags": {"b"}}, cls=JsonEncoder)
        '{"n": 3, "tags": ["b"]}'

    """

    def default(self, o: Any) -> Any:  # noqa: PLR0911
        """Convert an object to a type that `json` can encode.

        Args:
            o: Object to be serialized.

        Returns:
            A JSON-compatible representation of the object.

        """
        if isinstance(o, date | datetime | time):
            return o.isoformat()
        if isinstance(o, Path):
            return o.as_posix()
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, set | frozenset):
            return sorted(o, key=str)
        if isinstance(o, np.generic):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)
