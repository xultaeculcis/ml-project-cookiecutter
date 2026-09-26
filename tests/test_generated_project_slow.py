"""Slow end-to-end checks that run the tooling of a generated project. They need network access.

Run them with `make test-all` or `uv run pytest -m slow`.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import TYPE_CHECKING

import cruft
import pytest

from tests.conftest import MLPCC_ROOT
from tests.helpers import git

if TYPE_CHECKING:
    from pathlib import Path

    from tests.conftest import ProjectFactory

pytestmark = pytest.mark.slow

# Files that are not part of the template and must not be copied into the temporary template repository.
TEMPLATE_COPY_IGNORE = shutil.ignore_patterns(
    ".git", ".venv", ".idea", ".mypy_cache", ".ruff_cache", ".pytest_cache", "__pycache__", "docs-site", "site"
)


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a command with a clean uv environment and fail the test with its output on error."""
    exe = shutil.which(cmd[0])
    if exe is None:
        pytest.skip(f"{cmd[0]} is not installed")
    env = {key: value for key, value in os.environ.items() if key not in {"VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT"}}
    proc = subprocess.run(  # noqa: S603
        [exe, *cmd[1:]], cwd=cwd, env=env, capture_output=True, text=True, check=False
    )
    assert proc.returncode == 0, f"`{' '.join(cmd)}` failed:\n{proc.stdout}\n{proc.stderr}"
    return proc


@pytest.mark.parametrize(
    "overrides",
    [
        {},
        {"ml_stack": "none", "ci_provider": "none", "docker": "no", "agent_docs": "no"},
    ],
    ids=["default", "minimal"],
)
def test_generated_project_tooling(project_factory: ProjectFactory, overrides: dict[str, str]) -> None:
    project_dir = project_factory(**overrides)
    for target in ("init-project", "pc", "docs", "test"):
        _run(["make", target], cwd=project_dir)


def _commit_all(repo_dir: Path, message: str) -> None:
    for args in (("add", "."), ("commit", "--no-verify", "-m", message)):
        proc = git(repo_dir, *args)
        assert proc.returncode == 0, proc.stderr


def _template_repo(tmp_path: Path) -> Path:
    """Copy the working tree into a temporary git repository and return its path.

    cruft clones the template with git, so it only sees committed files. The copy makes the current (uncommitted)
    template visible to cruft.
    """
    template_dir = tmp_path / "template"
    shutil.copytree(MLPCC_ROOT, template_dir, ignore=TEMPLATE_COPY_IGNORE)
    proc = git(template_dir, "init", "--initial-branch=main")
    assert proc.returncode == 0, proc.stderr
    _commit_all(template_dir, "template")
    return template_dir


def _cruft_create(template_dir: Path, tmp_path: Path) -> Path:
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    project_dir: Path = cruft.create(
        str(template_dir), output_dir=output_dir, no_input=True, extra_context={"project_name": "cruft project"}
    )
    return project_dir


def test_cruft_create(tmp_path: Path) -> None:
    """F14: the template works with `cruft create`, so projects can later pull template changes with `cruft update`."""
    project_dir = _cruft_create(_template_repo(tmp_path), tmp_path)

    assert (project_dir / "pyproject.toml").is_file()
    cruft_state = json.loads((project_dir / ".cruft.json").read_text(encoding="utf-8"))
    assert cruft_state["context"]["cookiecutter"]["project_name"] == "cruft project"
    assert cruft.check(project_dir)


def test_cruft_update(tmp_path: Path) -> None:
    """F14: `cruft update` applies a later template change to a project.

    The post-generation hook runs `git init` also in the temporary copies that cruft generates for the diff. The
    `[tool.cruft] skip = [".git"]` setting in the template `pyproject.toml` keeps that `.git` directory out of the diff.
    """
    template_dir = _template_repo(tmp_path)
    project_dir = _cruft_create(template_dir, tmp_path)
    _commit_all(project_dir, "Add cruft state")

    marker = "Template update marker: cruft update works."
    readme = template_dir / "{{ cookiecutter.repo_name }}" / "README.md"
    readme.write_text(f"{readme.read_text(encoding='utf-8')}\n{marker}\n", encoding="utf-8")
    _commit_all(template_dir, "template change")

    assert not cruft.check(project_dir)
    assert cruft.update(project_dir, skip_apply_ask=True)

    assert marker in (project_dir / "README.md").read_text(encoding="utf-8")
    assert not (project_dir / "README.md.rej").exists()
    assert cruft.check(project_dir)
