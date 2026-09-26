{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
from pathlib import Path

from {{cookiecutter.package_name}}.consts import directories
from {{cookiecutter.package_name}}.consts.directories import CONFIGS_DIR, ROOT_DIR, find_root_dir

_PACKAGE = "{{cookiecutter.package_name}}"


def _make_project(root: Path) -> Path:
    (root / "src" / _PACKAGE).mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    return root


def test_root_dir_is_this_project() -> None:
    assert (ROOT_DIR / "pyproject.toml").is_file()
    assert Path(__file__).resolve().is_relative_to(ROOT_DIR)
    assert CONFIGS_DIR == ROOT_DIR / "configs"


def test_find_root_dir_walks_up_from_start(tmp_path: Path) -> None:
    root = _make_project(tmp_path / "project")
    nested = root / "notebooks" / "exploration"
    nested.mkdir(parents=True)
    assert find_root_dir(nested) == root.resolve()


def test_find_root_dir_ignores_other_projects(tmp_path: Path) -> None:
    other = tmp_path / "other"
    other.mkdir()
    (other / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    fallback = Path(directories.__file__).resolve().parents[3]
    assert find_root_dir(other) == fallback
