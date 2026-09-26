"""Logging consts.

Attributes:
    FORMAT (str): Default log format.

"""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
FORMAT = "%(asctime)s:%(pathname)s:%(levelname)s:%(lineno)d:%(message)s"
