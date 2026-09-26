"""Generic checks on the project generated with the default options."""

from __future__ import annotations

import re
import tomllib
from typing import TYPE_CHECKING

import pytest

from tests.helpers import (
    OLD_PLACEHOLDER_PATTERN,
    git,
    is_ci_file,
    project_files,
    project_text_files,
    unrendered_jinja_markers,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tests.conftest import ProjectFactory

PACKAGE = "dummy_project"

# Exact set of top-level entries for the default options (see cookiecutter.json).
EXPECTED_TOP_LEVEL = {
    ".dockerignore",
    ".env-sample",
    ".git",
    ".github",
    ".gitignore",
    ".pre-commit-config.yaml",
    ".python-version",
    "CLAUDE.md",
    "CONTEXT.md",
    "Dockerfile",
    "LICENSE",
    "Makefile",
    "README.md",
    "configs",
    "data",
    "docs",
    "mk",
    "mkdocs.yml",
    "notebooks",
    "pyproject.toml",
    "src",
    "tests",
}

EXPECTED_FILES = [
    ".github/dependabot.yaml",
    ".github/workflows/lock-files-update.yaml",
    ".github/workflows/nightly.yaml",
    ".github/workflows/pr.yaml",
    "configs/README.md",
    "configs/train.yaml",
    "data/auxiliary/.gitkeep",
    "data/inference/.gitkeep",
    "data/interim/.gitkeep",
    "data/processed/.gitkeep",
    "data/raw/.gitkeep",
    "docs/adr",
    "docs/api_ref/consts.md",
    "docs/api_ref/core.md",
    "docs/api_ref/utils.md",
    "docs/glossary.md",
    "docs/guides/contributing.md",
    "docs/guides/makefile-usage.md",
    "docs/guides/setup-dev-env.md",
    "docs/guides/tests.md",
    "docs/index.md",
    "mk/docker.mk",
    f"src/{PACKAGE}/__init__.py",
    f"src/{PACKAGE}/py.typed",
    f"src/{PACKAGE}/cli/__init__.py",
    f"src/{PACKAGE}/cli/entrypoint.py",
    f"src/{PACKAGE}/consts/__init__.py",
    f"src/{PACKAGE}/core/__init__.py",
    f"src/{PACKAGE}/core/settings.py",
    f"src/{PACKAGE}/utils/__init__.py",
    f"src/{PACKAGE}/utils/logging.py",
    f"src/{PACKAGE}/utils/mlflow.py",
    f"src/{PACKAGE}/utils/seed.py",
    f"src/{PACKAGE}/utils/serialization.py",
    "tests/__init__.py",
    "tests/conftest.py",
    "tests/unit/__init__.py",
    "tests/unit/test_configs.py",
]

UNEXPECTED_FILES = [
    f"src/{PACKAGE}/utils/gpu.py",
    "tests/unit/utils/test_gpu.py",
    ".azure-pipelines",
    ".github/workflows/zizmor-security-check.yaml",
    "aml",
    ".amlignore",
    "mk/aml.mk",
    f"src/{PACKAGE}/utils/torch.py",
    f"src/{PACKAGE}/lightning",
]


def test_expected_project_dir_name(dummy_project_dir: Path) -> None:
    assert dummy_project_dir.name == "dummy-project"


def test_top_level_entries(dummy_project_dir: Path) -> None:
    entries = {fp.name for fp in dummy_project_dir.iterdir()}
    assert entries == EXPECTED_TOP_LEVEL


@pytest.mark.parametrize("rel_path", EXPECTED_FILES)
def test_expected_file_exists(dummy_project_dir: Path, rel_path: str) -> None:
    assert (dummy_project_dir / rel_path).exists()


@pytest.mark.parametrize("rel_path", UNEXPECTED_FILES)
def test_unexpected_file_absent(dummy_project_dir: Path, rel_path: str) -> None:
    assert not (dummy_project_dir / rel_path).exists()


def test_readme(dummy_project_dir: Path) -> None:
    readme_txt = (dummy_project_dir / "README.md").read_text(encoding="utf-8")
    assert readme_txt.startswith("# dummy project\n\nA short description of the project\n")


def test_no_unrendered_jinja(dummy_project_dir: Path) -> None:
    offenders = {
        fp.relative_to(dummy_project_dir).as_posix(): markers
        for fp, content in project_text_files(dummy_project_dir).items()
        if (markers := unrendered_jinja_markers(content, allow_ci_expressions=is_ci_file(dummy_project_dir, fp)))
    }
    assert offenders == {}


def test_no_old_placeholders(dummy_project_dir: Path) -> None:
    offenders = [
        fp.relative_to(dummy_project_dir).as_posix()
        for fp, content in project_text_files(dummy_project_dir).items()
        if OLD_PLACEHOLDER_PATTERN.search(content)
    ]
    assert offenders == []


def test_text_files_checked(dummy_project_dir: Path) -> None:
    """Guard the Jinja check: it must see all important file types."""
    checked = {fp.relative_to(dummy_project_dir).as_posix() for fp in project_text_files(dummy_project_dir)}
    for rel_path in (
        ".env-sample",
        ".pre-commit-config.yaml",
        ".python-version",
        "Dockerfile",
        "Makefile",
        "mk/docker.mk",
        "mkdocs.yml",
        "pyproject.toml",
        ".github/workflows/pr.yaml",
        f"src/{PACKAGE}/__init__.py",
    ):
        assert rel_path in checked


@pytest.mark.parametrize("ci_provider", ["github", "azure"])
def test_ci_files_keep_ci_expressions(project_factory: ProjectFactory, ci_provider: str) -> None:
    project_dir = project_factory(ci_provider=ci_provider, zizmor="workflow-sarif")
    ci_dir = project_dir / (".github/workflows" if ci_provider == "github" else ".azure-pipelines")
    contents = {fp: fp.read_text(encoding="utf-8") for fp in ci_dir.rglob("*.yaml")}
    assert contents, f"no CI files in {ci_dir}"
    assert any("${{" in content for content in contents.values())
    for fp, content in contents.items():
        assert "{%" not in content, fp
        assert "%}" not in content, fp
        assert unrendered_jinja_markers(content, allow_ci_expressions=True) == [], fp


def test_env_sample_has_no_placeholders(dummy_project_dir: Path) -> None:
    content = (dummy_project_dir / ".env-sample").read_text(encoding="utf-8")
    assert "{{" not in content
    assert "<<" not in content
    assert "ENVIRONMENT=" in content


def test_pyproject_metadata(dummy_project_dir: Path) -> None:
    pyproject = tomllib.loads((dummy_project_dir / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    # PEP 503 normalized name: `dummy_project` and `dummy-project` are the same distribution.
    assert re.sub(r"[-_.]+", "-", project["name"]).lower() == "dummy-project"
    assert project["scripts"]["dummy-project"] == f"{PACKAGE}.cli.entrypoint:main"


def test_no_empty_directories(dummy_project_dir: Path) -> None:
    """Git does not track empty directories, so the template must not produce them."""
    empty_dirs = [
        fp.relative_to(dummy_project_dir).as_posix()
        for fp in dummy_project_dir.rglob("*")
        if fp.is_dir() and ".git" not in fp.relative_to(dummy_project_dir).parts and not any(fp.iterdir())
    ]
    assert empty_dirs == []


def test_git_initialized(dummy_project_dir: Path) -> None:
    assert (dummy_project_dir / ".git").is_dir(), "No .git directory found; repository not initialized."


def test_git_tracking_main_branch(dummy_project_dir: Path) -> None:
    proc = git(dummy_project_dir, "branch", "--show-current")
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "main"


def test_git_initial_commit(dummy_project_dir: Path) -> None:
    proc = git(dummy_project_dir, "log", "--format=%s")
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "Initial commit"


def test_git_working_tree_clean(dummy_project_dir: Path) -> None:
    proc = git(dummy_project_dir, "status", "--porcelain")
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == ""


def test_git_remote_uses_repo_url(dummy_project_dir: Path) -> None:
    proc = git(dummy_project_dir, "remote", "get-url", "origin")
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "https://github.com/some-dummy-author/dummy-project"


def test_git_tracks_all_generated_files(dummy_project_dir: Path) -> None:
    """B1: files like data/raw/.gitkeep must be committed, not ignored by the generated .gitignore."""
    proc = git(dummy_project_dir, "ls-files")
    assert proc.returncode == 0, proc.stderr
    tracked = set(proc.stdout.splitlines())
    for rel_path in (
        "data/raw/.gitkeep",
        "data/interim/.gitkeep",
        "data/processed/.gitkeep",
        "data/inference/.gitkeep",
        "data/auxiliary/.gitkeep",
        ".python-version",
        ".env-sample",
    ):
        assert rel_path in tracked
    untracked = {fp.relative_to(dummy_project_dir).as_posix() for fp in project_files(dummy_project_dir)} - tracked
    assert untracked == set()
