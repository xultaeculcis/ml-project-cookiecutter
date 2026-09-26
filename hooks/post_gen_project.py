"""Remove files for disabled options and initialize the git repository.

Cookiecutter renders this file with Jinja before it runs it. The hook runs inside the generated project directory.
The context is rendered as JSON inside a raw string (`load_context`), so quotes and backslashes in user values cannot
break the Python syntax of this file.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def load_context() -> dict[str, str]:
    """Return the rendered cookiecutter context.

    Returns:
        The cookiecutter context.

    """
    return json.loads(r"""{{ cookiecutter | jsonify }}""")  # type: ignore[no-any-return]


def removal_table(context: dict[str, str]) -> list[tuple[bool, list[str]]]:
    """Return the paths to remove for each option.

    Args:
        context: The cookiecutter context.

    Returns:
        A list of (condition, paths to remove when the condition is true). Paths are relative to the project root.

    """
    package_name = context["package_name"]
    ml_stack = context["ml_stack"]
    return [
        (context["ci_provider"] != "github", [".github/workflows/pr.yaml", ".github/workflows/nightly.yaml"]),
        (context["ci_provider"] != "azure", [".azure-pipelines"]),
        (context["dependabot"] == "no", [".github/dependabot.yaml"]),
        (context["lock_update_workflow"] == "no", [".github/workflows/lock-files-update.yaml"]),
        (context["zizmor"] != "workflow-sarif", [".github/workflows/zizmor-security-check.yaml"]),
        (context["docker"] == "no", ["Dockerfile", ".dockerignore", "mk/docker.mk"]),
        (context["azure_ml"] == "no", ["aml", "mk/aml.mk", ".amlignore", "docs/guides/azure-ml.md"]),
        (context["agent_docs"] == "no", ["CLAUDE.md", "CONTEXT.md", "docs/glossary.md", "docs/adr"]),
        (
            ml_stack not in {"torch", "lightning"},
            [f"src/{package_name}/utils/torch.py", "tests/unit/utils/test_torch.py"],
        ),
        (
            ml_stack != "lightning",
            [f"src/{package_name}/lightning", "tests/unit/lightning", "configs/lightning", "docs/api_ref/lightning.md"],
        ),
    ]


# Directories to remove when they are empty after the removals. Order matters: children first.
PRUNE_IF_EMPTY = [".github/workflows", ".github", "mk"]


def remove_path(path: Path) -> None:
    """Remove a file or a directory tree. Do nothing if the path does not exist.

    Args:
        path: The path to remove.

    """
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def remove_disabled_features(project_dir: Path, context: dict[str, str]) -> None:
    """Remove the files of all disabled options and prune empty directories.

    Args:
        project_dir: The generated project directory.
        context: The cookiecutter context.

    """
    for condition, paths in removal_table(context):
        if condition:
            for rel_path in paths:
                remove_path(project_dir / rel_path)

    for rel_dir in PRUNE_IF_EMPTY:
        directory = project_dir / rel_dir
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()


def warn(message: str) -> None:
    """Print a warning to stderr.

    Args:
        message: The warning text.

    """
    print(f"WARNING: {message}", file=sys.stderr)  # noqa: T201


def run_git(git: str, *args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a git command and capture its output. Never raise on a non-zero exit code.

    Args:
        git: The path to the git executable.
        *args: The git arguments.
        cwd: The working directory.

    Returns:
        The completed process.

    """
    return subprocess.run([git, *args], cwd=cwd, capture_output=True, text=True, check=False)  # noqa: S603


def init_git_repo(project_dir: Path, repo_url: str) -> None:
    """Initialize a git repository on `main`, add the remote and make the initial commit if possible.

    This function never raises. A git problem must not make cookiecutter delete the generated project.

    Args:
        project_dir: The generated project directory.
        repo_url: The URL of the `origin` remote.

    """
    git = shutil.which("git")
    if git is None:
        warn("git is not installed. Skipping repository initialization.")
        return

    if run_git(git, "init", "--initial-branch=main", cwd=project_dir).returncode != 0:
        # git < 2.28 does not know --initial-branch
        if run_git(git, "init", cwd=project_dir).returncode != 0:
            warn("`git init` failed. Skipping repository initialization.")
            return
        run_git(git, "symbolic-ref", "HEAD", "refs/heads/main", cwd=project_dir)

    if run_git(git, "remote", "add", "origin", repo_url, cwd=project_dir).returncode != 0:
        warn(f"Could not add the git remote. Run `git remote add origin {repo_url}` manually.")

    add = run_git(git, "add", ".", cwd=project_dir)
    if add.returncode != 0:
        warn(f"`git add .` failed:\n{add.stderr.strip()}")
        return

    commit = run_git(git, "commit", "--no-verify", "-m", "Initial commit", cwd=project_dir)
    if commit.returncode != 0:
        warn(
            "Could not make the initial commit. The files are staged.\n"
            "Configure your git identity (`git config --global user.name ...` and "
            "`git config --global user.email ...`) and run `git commit -m 'Initial commit'`.\n"
            f"git output:\n{commit.stderr.strip() or commit.stdout.strip()}"
        )


def print_next_steps(repo_name: str) -> None:
    """Print the next steps for the user.

    Args:
        repo_name: The repository (directory) name.

    """
    print(  # noqa: T201
        "\nProject created. Next steps:\n"
        f"  cd {repo_name}\n"
        "  make init-project   # create the uv env, lock file and install pre-commit hooks\n"
        "  make help           # show all make targets\n"
    )


def main() -> None:
    """Run the post-generation steps."""
    context = load_context()
    project_dir = Path.cwd()
    remove_disabled_features(project_dir, context)
    init_git_repo(project_dir, context["repo_url"])
    print_next_steps(context["repo_name"])


if __name__ == "__main__":
    main()
