"""Run the CLI with `python -m {{cookiecutter.package_name}}`."""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
from {{cookiecutter.package_name}}.cli.entrypoint import main

if __name__ == "__main__":
    main()
