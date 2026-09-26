{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import json
from datetime import UTC, date, datetime, time
from enum import Enum, StrEnum
from pathlib import Path
from uuid import UUID

import numpy as np
import pytest

from {{cookiecutter.package_name}}.utils.serialization import JsonEncoder


class Color(Enum):
    red = 1


class Split(StrEnum):
    train = "train"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (date(2023, 4, 10), '"2023-04-10"'),
        (datetime(2023, 4, 10, 15, 30, 45, tzinfo=UTC), '"2023-04-10T15:30:45+00:00"'),
        (time(15, 30), '"15:30:00"'),
        (Path("/home/user/documents"), '"/home/user/documents"'),
        (Color.red, "1"),
        (Split.train, '"train"'),
        (UUID("12345678-1234-5678-1234-567812345678"), '"12345678-1234-5678-1234-567812345678"'),
        ({"b", "a"}, '["a", "b"]'),
        (frozenset({2, 1}), "[1, 2]"),
        (np.int64(3), "3"),
        (np.float32(0.5), "0.5"),
        (np.True_, "true"),
        (np.array([[1, 2], [3, 4]]), "[[1, 2], [3, 4]]"),
    ],
    ids=lambda v: type(v).__name__,
)
def test_serialization(value: object, expected: str) -> None:
    assert json.dumps(value, cls=JsonEncoder) == expected


def test_nested_serialization() -> None:
    payload = {"path": Path("a/b"), "values": np.arange(3), "when": date(2024, 1, 2)}
    assert json.loads(json.dumps(payload, cls=JsonEncoder)) == {
        "path": "a/b",
        "values": [0, 1, 2],
        "when": "2024-01-02",
    }


def test_unsupported_type_serialization() -> None:
    with pytest.raises(TypeError):
        json.dumps({"key": complex(1, 2)}, cls=JsonEncoder)
