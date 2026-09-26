"""Experiment reproducibility related consts.

Attributes:
    SEED (int): Random seed - 42.

"""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
SEED = 42
