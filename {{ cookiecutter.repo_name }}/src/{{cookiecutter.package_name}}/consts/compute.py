"""Compute related consts.

Attributes:
    CPU_COUNT (int): Number of physical CPU cores. Falls back to the logical core count, then to 1.
    EPS (float): Floating point error.

"""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import os

import psutil

CPU_COUNT: int = psutil.cpu_count(logical=False) or os.cpu_count() or 1
EPS = 1e-8
