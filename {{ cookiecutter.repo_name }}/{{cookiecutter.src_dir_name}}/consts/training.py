"""Training related consts."""

from __future__ import annotations

from enum import StrEnum


class Stages(StrEnum):
    """Enum representing training stages."""

    train = "train"
    val = "val"
    test = "test"
    predict = "predict"
