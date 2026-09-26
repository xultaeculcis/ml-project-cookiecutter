"""Update the pinned tool versions inside the template directory.

Dependabot, `pre-commit autoupdate` and `gha-update` cannot read the template files directly, because the files contain
Jinja. This script works around it:

1. pre-commit hooks: generate a project, run `pre-commit autoupdate` in it, and copy the new `rev` values back into the
   template `.pre-commit-config.yaml` (and the `ruff==` pin in the template `pyproject.toml`). The uv version in the
   template `Dockerfile` and in the Azure Pipelines `uvVersion` parameter follows the `uv-pre-commit` rev.
2. GitHub Actions: copy the template workflows into a temporary git repository, run `gha-update` there (it only edits
   the `uses:` lines, so Jinja does not matter), and copy the files back.

Run from the repository root: `uv run python .github/scripts/update_template_deps.py`.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from cookiecutter.main import cookiecutter

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR_NAME = "{{ cookiecutter.repo_name }}"
RUFF_REPO = "https://github.com/astral-sh/ruff-pre-commit"
UV_REPO = "https://github.com/astral-sh/uv-pre-commit"
# Template files that pin the uv version, relative to the template directory.
DOCKERFILE = "Dockerfile"
AZURE_UV_STEP = ".azure-pipelines/steps/uv-env-create.yaml"
# `FROM ghcr.io/astral-sh/uv:0.12.19 AS uv`. Only a plain version tag matches, not tags such as `python3.13-trixie`.
DOCKERFILE_UV_PATTERN = re.compile(r"(ghcr\.io/astral-sh/uv:)\d+\.\d+\.\d+(?=\s)")
# The `default` of the `uvVersion` parameter: `- name: uvVersion` followed by `default: "0.12.19"` a few lines below.
AZURE_UV_PATTERN = re.compile(r"(-\s+name:\s+uvVersion\s*\n(?:[ \t]+[^\n]*\n){0,5}?[ \t]+default:\s+)\"[^\"\n]*\"")
# Options that enable every optional pre-commit hook.
GENERATION_CONTEXT = {"zizmor": "pre-commit"}
GIT_IDENTITY = {
    "GIT_AUTHOR_NAME": "template-deps-update",
    "GIT_AUTHOR_EMAIL": "template-deps-update@users.noreply.github.com",
    "GIT_COMMITTER_NAME": "template-deps-update",
    "GIT_COMMITTER_EMAIL": "template-deps-update@users.noreply.github.com",
}


def run(*cmd: str, cwd: Path) -> None:
    """Run a command and raise on failure.

    Args:
        *cmd: The command and its arguments.
        cwd: The working directory.

    """
    exe = shutil.which(cmd[0])
    if exe is None:
        msg = f"{cmd[0]} is not installed"
        raise RuntimeError(msg)
    env = {**os.environ, **GIT_IDENTITY}
    subprocess.run([exe, *cmd[1:]], cwd=cwd, env=env, check=True)  # noqa: S603


def pre_commit_revs(config_fp: Path) -> dict[str, str]:
    """Return a mapping of repo URL to rev from a rendered pre-commit config.

    Args:
        config_fp: The path to the `.pre-commit-config.yaml` file.

    Returns:
        The mapping of repo URL to rev. Local and meta repos are skipped.

    """
    config = yaml.safe_load(config_fp.read_text(encoding="utf-8"))
    return {repo["repo"]: str(repo["rev"]) for repo in config["repos"] if "rev" in repo}


def apply_revs(template_text: str, revs: dict[str, str]) -> str:
    """Replace the `rev` value that follows each `- repo: <url>` line in the (Jinja) template text.

    Args:
        template_text: The template `.pre-commit-config.yaml` content.
        revs: The mapping of repo URL to the new rev.

    Returns:
        The updated template content.

    """
    for url, rev in revs.items():
        template_text = _set_rev(template_text, url, rev)
    return template_text


def _set_rev(template_text: str, url: str, rev: str) -> str:
    pattern = re.compile(rf"(-\s+repo:\s+{re.escape(url)}\s*\n\s+rev:\s+)(\S+)")
    return pattern.sub(lambda match: f"{match.group(1)}{rev}", template_text)


def set_dockerfile_uv_version(text: str, version: str) -> str:
    """Set the version tag of the `ghcr.io/astral-sh/uv` image in the (Jinja) template Dockerfile.

    Args:
        text: The template Dockerfile content.
        version: The uv version, with or without a leading `v`.

    Returns:
        The updated content. Jinja expressions are not changed.

    """
    return DOCKERFILE_UV_PATTERN.sub(lambda match: f"{match.group(1)}{version.removeprefix('v')}", text)


def set_azure_uv_version(text: str, version: str) -> str:
    """Set the default of the `uvVersion` parameter in the (Jinja) template Azure Pipelines step file.

    Args:
        text: The template `uv-env-create.yaml` content.
        version: The uv version, with or without a leading `v`.

    Returns:
        The updated content. Jinja expressions are not changed.

    """
    return AZURE_UV_PATTERN.sub(lambda match: f'{match.group(1)}"{version.removeprefix("v")}"', text)


def sync_uv_version(template_dir: Path, version: str) -> None:
    """Set the uv version in the template Dockerfile and Azure Pipelines step to the `uv-pre-commit` rev.

    Args:
        template_dir: The template directory.
        version: The uv version.

    """
    for rel_path, setter in ((DOCKERFILE, set_dockerfile_uv_version), (AZURE_UV_STEP, set_azure_uv_version)):
        fp = template_dir / rel_path
        if fp.is_file():
            fp.write_text(setter(fp.read_text(encoding="utf-8"), version), encoding="utf-8")


def update_pre_commit(root: Path, tmp_dir: Path) -> None:
    """Update the template pre-commit hook revs and the matching ruff pin.

    Args:
        root: The cookiecutter repository root.
        tmp_dir: A temporary directory for the generated project.

    """
    template_pre_commit = root / TEMPLATE_DIR_NAME / ".pre-commit-config.yaml"
    template_pyproject = root / TEMPLATE_DIR_NAME / "pyproject.toml"
    project_dir = Path(
        cookiecutter(str(root), no_input=True, output_dir=str(tmp_dir), extra_context=GENERATION_CONTEXT)
    )
    run("uvx", "pre-commit", "autoupdate", cwd=project_dir)
    revs = pre_commit_revs(project_dir / ".pre-commit-config.yaml")
    template_pre_commit.write_text(apply_revs(template_pre_commit.read_text(encoding="utf-8"), revs), encoding="utf-8")

    if ruff_rev := revs.get(RUFF_REPO):
        pyproject = template_pyproject.read_text(encoding="utf-8")
        pyproject = re.sub(r'"ruff==[^"]+"', f'"ruff=={ruff_rev.removeprefix("v")}"', pyproject)
        template_pyproject.write_text(pyproject, encoding="utf-8")

    if uv_rev := revs.get(UV_REPO):
        sync_uv_version(root / TEMPLATE_DIR_NAME, uv_rev)


def update_github_actions(root: Path, tmp_dir: Path) -> None:
    """Pin the template GitHub Actions to the latest release SHAs with gha-update.

    Args:
        root: The cookiecutter repository root.
        tmp_dir: A temporary directory for the scratch git repository.

    """
    template_workflows = root / TEMPLATE_DIR_NAME / ".github" / "workflows"
    if not template_workflows.is_dir():
        return
    scratch_workflows = tmp_dir / ".github" / "workflows"
    shutil.copytree(template_workflows, scratch_workflows)
    run("git", "init", "--quiet", cwd=tmp_dir)
    run("uvx", "gha-update", cwd=tmp_dir)
    for fp in scratch_workflows.iterdir():
        shutil.copyfile(fp, template_workflows / fp.name)


def main() -> int:
    """Update the template pre-commit hooks and GitHub Actions.

    Returns:
        The exit code.

    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Cookiecutter repository root.")
    root: Path = parser.parse_args().root.resolve()
    with tempfile.TemporaryDirectory() as pre_commit_tmp, tempfile.TemporaryDirectory() as actions_tmp:
        update_pre_commit(root, Path(pre_commit_tmp))
        update_github_actions(root, Path(actions_tmp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
