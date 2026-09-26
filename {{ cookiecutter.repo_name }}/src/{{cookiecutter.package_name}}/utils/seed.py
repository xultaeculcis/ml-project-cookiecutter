"""Reproducibility utils."""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import os
import random

import numpy as np
{%- if cookiecutter.ml_stack in ["torch", "lightning"] %}
import torch
{%- endif %}

from {{cookiecutter.package_name}} import consts


def seed_everything(seed: int = consts.reproducibility.SEED) -> int:
{%- if cookiecutter.ml_stack in ["torch", "lightning"] %}
    """Seed the random number generators of `random`, `numpy` and `torch` (CPU and all CUDA devices).
{%- else %}
    """Seed the random number generators of `random`, `numpy` and, if installed, `torch`.
{%- endif %}

    The function also sets `PYTHONHASHSEED`. This has an effect only on Python processes started after the call,
    for example data loader workers.

    Args:
        seed: The random seed.

    Returns:
        The seed that was used.

    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)  # noqa: NPY002
{%- if cookiecutter.ml_stack not in ["torch", "lightning"] %}

    try:
        # torch is not a dependency of this project. Seed it only if it is installed.
        import torch  # noqa: PLC0415
    except ImportError:
        return seed
{%- endif %}

    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    return seed
