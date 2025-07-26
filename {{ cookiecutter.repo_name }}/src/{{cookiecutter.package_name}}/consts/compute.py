"""Compute related consts.

Attributes:
    CPU_COUNT (int): CPU count.
    EPS (float): Floating point error.

"""

from __future__ import annotations

import psutil

CPU_COUNT = psutil.cpu_count(logical=False)
EPS = 1e-8
