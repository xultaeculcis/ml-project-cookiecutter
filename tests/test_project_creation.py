from __future__ import annotations

import subprocess  # noqa: S404, RUF100
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.conftest import COOKIECUTTER_CONFIG

if TYPE_CHECKING:
    from collections.abc import Callable


def no_curlies(fp: Path) -> bool:
    data = fp.read_text(encoding="utf-8")
    template_strings = ["{{", "}}", "{%", "%}"]
    template_strings_in_file = [s in data for s in template_strings]
    return not any(template_strings_in_file)


def test_expected_project_dir_name(dummy_project_dir: Path) -> None:
    assert dummy_project_dir.name == "dummy-project"


def test_expected_project_dir_structure(dummy_project_dir: Path) -> None:
    expected_items = [
        ".azure-pipelines",
        ".azure-pipelines/jobs",
        ".azure-pipelines/jobs/code-qa.yaml",
        ".azure-pipelines/jobs/test-suite.yaml",
        ".azure-pipelines/steps",
        ".azure-pipelines/steps/code-qa.yaml",
        ".azure-pipelines/steps/uv-env-create.yaml",
        ".azure-pipelines/steps/test-suite.yaml",
        ".azure-pipelines/pr-pipeline.yaml",
        ".github",
        ".github/workflows",
        ".github/workflows/lock-files-update.yaml",
        ".github/workflows/zizmor-security-check.yaml",
        "data",
        "data/auxiliary",
        "data/inference",
        "data/interim",
        "data/processed",
        "data/raw",
        "docs",
        "docs/api_ref",
        "docs/api_ref/consts.md",
        "docs/api_ref/core.md",
        "docs/api_ref/utils.md",
        "docs/guides/contributing.md",
        "docs/guides/makefile-usage.md",
        "docs/guides/setup-dev-env.md",
        "docs/guides/tests.md",
        "docs/index.md",
        "notebooks",
        "src",
        "src/dummy_project",
        "src/dummy_project/__init__.py",
        "src/dummy_project/py.typed",
        "src/dummy_project/consts",
        "src/dummy_project/consts/__init__.py",
        "src/dummy_project/consts/directories.py",
        "src/dummy_project/consts/logging.py",
        "src/dummy_project/core",
        "src/dummy_project/core/__init__.py",
        "src/dummy_project/core/settings.py",
        "src/dummy_project/utils/__init__.py",
        "src/dummy_project/utils/gpu.py",
        "src/dummy_project/utils/logging.py",
        "src/dummy_project/utils/mlflow.py",
        "src/dummy_project/utils/serialization.py",
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
        "tests/unit/core/test_settings.py",
        "tests/unit/utils/test_gpu.py",
        "tests/unit/utils/test_logging.py",
        "tests/unit/utils/test_mlflow.py",
        "tests/unit/utils/test_serialization.py",
        ".env-sample",
        ".gitignore",
        ".pre-commit-config.yaml",
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


@pytest.mark.parametrize(
    "fp",
    [
        ".azure-pipelines/pr-pipeline.yaml",
        ".azure-pipelines/steps/test-suite.yaml",
        ".github/workflows/lock-files-update.yaml",
        ".github/workflows/zizmor-security-check.yaml",
    ],
)
def test_ci_pipelines_have_proper_placeholders(dummy_project_dir: Path, fp: str) -> None:
    content = (dummy_project_dir / fp).read_text()
    assert "$<<" not in content
    assert ">>" not in content
    assert "${{" in content
    assert "}}" in content


@pytest.mark.parametrize("fp", [".env-sample"])
def test_env_files_have_proper_placeholders(dummy_project_dir: Path, fp: str) -> None:
    content = (dummy_project_dir / fp).read_text()
    assert "<<" not in content
    assert ">>" not in content
    assert "{{" in content
    assert "}}" in content


@pytest.mark.parametrize("license_type", COOKIECUTTER_CONFIG["license"], ids=COOKIECUTTER_CONFIG["license"])
def test_license(dummy_project_factory: Callable[[str], Path], license_type: str) -> None:
    project_dir = dummy_project_factory(license_type)
    expected_content = (Path(__file__).parent / "licenses" / f"{license_type}.txt").read_text()
    expected_content = expected_content.format(year=datetime.now(tz=UTC).year)
    if license_type != "No license file":
        assert expected_content in (project_dir / "LICENSE").read_text()
    else:
        assert (project_dir / "LICENSE").read_text() == expected_content


def test_git_initialized(dummy_project_dir: Path) -> None:
    git_dir = dummy_project_dir / ".git"
    assert git_dir.is_dir(), "No .git directory found; repository not initialized."


def test_git_tracking_main_branch(dummy_project_dir: Path) -> None:
    proc = subprocess.run(
        ["git", "branch", "--show-current"],  # noqa: S607
        cwd=dummy_project_dir.as_posix(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, f"Failed to determine current Git branch: {proc.stderr}"
    assert proc.stdout.strip() == "main", f"Expected 'main' branch but got '{proc.stdout.strip()}'"
