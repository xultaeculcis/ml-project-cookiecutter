"""Shared helpers for the template tests."""

from __future__ import annotations

import re
import shutil
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# GitHub Actions / Azure Pipelines expressions, e.g. `${{ secrets.TOKEN }}`
CI_EXPRESSION_PATTERN = re.compile(r"\$\{\{.*?\}\}", flags=re.DOTALL)
# Unrendered Jinja expressions, statements and comments. A lone `}}` (nested Python dict) is not a match.
JINJA_PATTERNS = (
    re.compile(r"\{\{.*?\}\}", flags=re.DOTALL),
    re.compile(r"\{%.*?%\}", flags=re.DOTALL),
    re.compile(r"\{#.*?#\}", flags=re.DOTALL),
)
# Leftovers of the removed `<<X>>` placeholder mechanism
OLD_PLACEHOLDER_PATTERN = re.compile(r"<<[A-Za-z.\-_ ]+>>")
CI_DIRS = (".github", ".azure-pipelines", "aml")


def project_files(project_dir: Path) -> list[Path]:
    """Return all files in the generated project, without the `.git` directory.

    Args:
        project_dir: The generated project directory.

    Returns:
        A sorted list of file paths.

    """
    return sorted(
        fp for fp in project_dir.rglob("*") if fp.is_file() and ".git" not in fp.relative_to(project_dir).parts
    )


def project_text_files(project_dir: Path) -> dict[Path, str]:
    """Return the content of all text (UTF-8 decodable) files in the generated project.

    Args:
        project_dir: The generated project directory.

    Returns:
        A mapping of file path to file content.

    """
    result: dict[Path, str] = {}
    for fp in project_files(project_dir):
        try:
            result[fp] = fp.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
    return result


def is_ci_file(project_dir: Path, fp: Path) -> bool:
    """Return True if the file is a CI definition that can contain `${{ ... }}` expressions.

    Args:
        project_dir: The generated project directory.
        fp: The file path.

    Returns:
        True for files under `.github/` or `.azure-pipelines/`.

    """
    return fp.relative_to(project_dir).parts[0] in CI_DIRS


def unrendered_jinja_markers(content: str, *, allow_ci_expressions: bool = False) -> list[str]:
    """Return the unrendered Jinja snippets that are still in the content.

    Args:
        content: The file content.
        allow_ci_expressions: If True, ignore GitHub/Azure `${{ ... }}` expressions.

    Returns:
        The list of snippets found.

    """
    if allow_ci_expressions:
        content = CI_EXPRESSION_PATTERN.sub("", content)
    return [match.group(0) for pattern in JINJA_PATTERNS for match in pattern.finditer(content)]


def git(project_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command in the project directory.

    Args:
        project_dir: The generated project directory.
        *args: The git arguments.

    Returns:
        The completed process.

    """
    git_exe = shutil.which("git")
    assert git_exe is not None, "git is not installed"
    return subprocess.run(  # noqa: S603
        [git_exe, *args], cwd=project_dir, capture_output=True, text=True, check=False
    )
