"""The constants to be used across the project."""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
from {{cookiecutter.package_name}}.consts import compute, directories, logging, reproducibility, tracking, training

__all__ = [
    "compute",
    "directories",
    "logging",
    "reproducibility",
    "tracking",
    "training",
]
