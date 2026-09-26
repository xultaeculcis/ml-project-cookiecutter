"""Training related consts."""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
from enum import StrEnum


class Stages(StrEnum):
    """Enum representing training stages."""

    train = "train"
    val = "val"
    test = "test"
    predict = "predict"
