from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable

import pytest

LICENSES = ["MIT", "Apache 2.0", "BSD-3-Clause", "Beerware", "GLWTS", "Proprietary", "Empty license file"]


def no_curlies(fp: Path) -> bool:
    data = fp.read_text()
    template_strings = ["{{", "}}", "{%", "%}"]
    template_strings_in_file = [s in data for s in template_strings]
    return not any(template_strings_in_file)


def test_expected_project_dir_name(dummy_project_dir: Path) -> None:
    assert dummy_project_dir.name == "dummy-project"


def test_expected_project_dir_structure(dummy_project_dir: Path) -> None:
    expected_items = [
        "data",
        "data/auxiliary",
        "data/inference",
        "data/interim",
        "data/processed",
        "data/raw",
        "docs",
        "docs/api_ref",
        "docs/api_ref/consts.md",
        "docs/api_ref/core/configs.md",
        "docs/api_ref/core/settings.md",
        "docs/api_ref/utils.md",
        "docs/guides/contributing.md",
        "docs/guides/makefile-usage.md",
        "docs/guides/setup-dev-env.md",
        "docs/guides/tests.md",
        "docs/index.md",
        "dummy_project",
        "dummy_project/__init__.py",
        "dummy_project/py.typed",
        "dummy_project/consts",
        "dummy_project/consts/__init__.py",
        "dummy_project/consts/directories.py",
        "dummy_project/consts/logging.py",
        "dummy_project/core",
        "dummy_project/core/__init__.py",
        "dummy_project/core/configs",
        "dummy_project/core/configs/base.py",
        "dummy_project/core/configs/argument_parsing.py",
        "dummy_project/core/settings.py",
        "dummy_project/utils/__init__.py",
        "dummy_project/utils/gpu.py",
        "dummy_project/utils/logging.py",
        "dummy_project/utils/mlflow.py",
        "dummy_project/utils/serialization.py",
        "notebooks",
        "tests",
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/e2e",
        "tests/e2e/__init__.py",
        "tests/e2e/test_dummy.py",
        "tests/integration",
        "tests/integration/__init__.py",
        "tests/integration/test_dummy.py",
        "tests/unit",
        "tests/unit/__init__.py",
        "tests/unit/core",
        "tests/unit/core/configs",
        "tests/unit/core/configs/__init__.py",
        "tests/unit/core/configs/test_argument_parsing.py",
        "tests/unit/core/configs/test_config_base.py",
        "tests/unit/core/test_settings.py",
        "tests/unit/utils/test_gpu.py",
        "tests/unit/utils/test_logging.py",
        "tests/unit/utils/test_mlflow.py",
        "tests/unit/utils/test_serialization.py",
        ".env-sample",
        ".gitignore",
        ".pre-commit-config.yaml",
        "env.yaml",
        "env-dev.yaml",
        "LICENSE",
        "Makefile",
        "mkdocs.yml",
        "pyproject.toml",
        "README.md",
    ]
    fps = [fp.relative_to(dummy_project_dir).as_posix() for fp in dummy_project_dir.rglob("*")]
    diff = set(expected_items).difference(fps)
    assert diff == set()


def test_readme(dummy_project_dir: Path) -> None:
    readme_txt = (dummy_project_dir / "README.md").read_text()
    assert no_curlies(dummy_project_dir / "README.md")
    assert readme_txt.startswith("# dummy project\n\nA short description of the project\n")


def test_makefile(dummy_project_dir: Path) -> None:
    assert no_curlies(dummy_project_dir / "Makefile")


def test_source_files(dummy_project_dir: Path) -> None:
    for fp in dummy_project_dir.rglob("*.py"):
        assert no_curlies(fp)


def test_documentation_files(dummy_project_dir: Path) -> None:
    for fp in dummy_project_dir.rglob("*.md"):
        assert no_curlies(fp)
    assert no_curlies(dummy_project_dir / "mkdocs.yml")


def test_dot_env_sample_has_placeholders(dummy_project_dir: Path) -> None:
    content = (dummy_project_dir / ".env-sample").read_text()
    assert content == "ENVIRONMENT={{ENVIRONMENT}}\n"


@pytest.mark.parametrize("license_type", LICENSES, ids=LICENSES)
def test_license(dummy_project_factory: Callable[[str], Path], license_type: str) -> None:
    project_dir = dummy_project_factory(license_type)
    expected_content = (Path(__file__).parent / "licenses" / f"{license_type}.txt").read_text()
    expected_content = expected_content.format(year=datetime.utcnow().year)  # noqa: DTZ003
    if license_type != "No license file":
        assert expected_content in (project_dir / "LICENSE").read_text()
    else:
        assert (project_dir / "LICENSE").read_text() == expected_content
