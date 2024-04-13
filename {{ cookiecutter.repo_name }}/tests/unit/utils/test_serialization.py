import json
from datetime import date, datetime
from pathlib import Path

import pytest

from {{cookiecutter.src_dir_name}}.utils.serialization import JsonEncoder


def test_date_serialization() -> None:
    test_date = date(2023, 4, 10)
    expected = '"2023-04-10"'
    assert json.dumps(test_date, cls=JsonEncoder) == expected


def test_datetime_serialization() -> None:
    test_datetime = datetime(2023, 4, 10, 15, 30, 45)
    expected = '"2023-04-10T15:30:45"'
    assert json.dumps(test_datetime, cls=JsonEncoder) == expected


def test_path_serialization() -> None:
    test_path = Path("/home/user/documents")
    expected = '"/home/user/documents"'
    assert json.dumps(test_path, cls=JsonEncoder) == expected


def test_unsupported_type_serialization() -> None:
    with pytest.raises(TypeError):
        json.dumps({"key": complex(1, 2)}, cls=JsonEncoder)
