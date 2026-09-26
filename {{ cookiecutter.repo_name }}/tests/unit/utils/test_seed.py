{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import os
import random

import numpy as np
import pytest
{%- if cookiecutter.ml_stack in ["torch", "lightning"] %}
import torch
{%- endif %}

from {{cookiecutter.package_name}} import consts
from {{cookiecutter.package_name}}.utils.seed import seed_everything


@pytest.fixture(autouse=True)
def _restore_pythonhashseed(monkeypatch: pytest.MonkeyPatch) -> None:
    # Record the current value, so monkeypatch restores it after the test.
    monkeypatch.setenv("PYTHONHASHSEED", os.environ.get("PYTHONHASHSEED", "0"))


def test_returns_seed_and_sets_pythonhashseed() -> None:
    assert seed_everything(123) == 123
    assert os.environ["PYTHONHASHSEED"] == "123"


def test_default_seed() -> None:
    assert seed_everything() == consts.reproducibility.SEED


def _draw() -> tuple[float, float{% if cookiecutter.ml_stack in ["torch", "lightning"] %}, float{% endif %}]:
    return (
        random.random(),  # noqa: S311
        float(np.random.rand()),  # noqa: NPY002
{%- if cookiecutter.ml_stack in ["torch", "lightning"] %}
        float(torch.rand(1).item()),
{%- endif %}
    )


def test_same_seed_gives_same_numbers() -> None:
    seed_everything(7)
    first = _draw()
    seed_everything(7)
    assert _draw() == first


def test_different_seed_gives_different_numbers() -> None:
    seed_everything(7)
    first = _draw()
    seed_everything(8)
    assert _draw() != first
