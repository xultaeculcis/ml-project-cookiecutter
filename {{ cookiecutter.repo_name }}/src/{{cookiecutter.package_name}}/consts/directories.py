"""Project directory related consts.

`ROOT_DIR` is found in this order:

1. Walk up from the current working directory. The first directory that holds a `pyproject.toml` file and a
   `src/{{cookiecutter.package_name}}` directory is the project root. This works for a source checkout, a Docker image
   and an Azure ML code snapshot, as long as the process starts inside the project.
2. If no such directory is found, use the directory three levels above this file. This is correct for an editable
   install (`uv sync`), but not for a wheel installed into `site-packages`.

Attributes:
    ROOT_DIR (Path): Project root directory.
    SRC_DIR (Path): Project src directory.
    TESTS_DIR (Path): Project test directory.
    DATA_DIR (Path): Project data directory.
    CONFIGS_DIR (Path): Project configs directory.

"""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
from pathlib import Path

_PACKAGE_NAME = "{{cookiecutter.package_name}}"


def find_root_dir(start: Path | None = None) -> Path:
    """Find the project root directory.

    Args:
        start: The directory to start the search from. Defaults to the current working directory.

    Returns:
        The first directory at or above `start` that holds `pyproject.toml` and `src/<package>`. If there is none,
        the directory three levels above this file.

    """
    start = (start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "src" / _PACKAGE_NAME).is_dir():
            return candidate
    return Path(__file__).resolve().parents[3]


ROOT_DIR = find_root_dir()
SRC_DIR = ROOT_DIR / "src"
TESTS_DIR = ROOT_DIR / "tests"
DATA_DIR = ROOT_DIR / "data"
CONFIGS_DIR = ROOT_DIR / "configs"
