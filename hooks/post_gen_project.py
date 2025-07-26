from __future__ import annotations

import re
import subprocess  # noqa: S404, RUF100
from pathlib import Path


def replace_placeholders(file_path: Path) -> None:
    content = file_path.read_text(encoding="utf-8")
    placeholders = re.findall(r"<<([A-Za-z.\-_ ]+)>>", content)

    for placeholder in placeholders:
        # Don't use f-strings otherwise Jinja will throw error
        replacement = "{" + "{" + placeholder + "}" + "}"
        content = content.replace(f"<<{placeholder}>>", replacement)

    file_path.write_text(content, encoding="utf-8")


def init_git_repo() -> None:
    # Initialize git repo on 'main' branch (Git >= 2.28 required)
    subprocess.run(["git", "init", "--initial-branch=main"], check=True)  # noqa: S607

    # Stage and commit
    subprocess.run(["git", "add", "."], check=True)  # noqa: S607
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)  # noqa: S607


def configure_remote() -> None:
    subprocess.run(["git", "remote", "add", "origin", "{{ cookiecutter.repo_url }}"], check=True)  # noqa: S607
    # Optionally rename your default branch to 'main'
    subprocess.run(["git", "branch", "-M", "main"], check=True)  # noqa: S607


def main() -> None:
    replace_placeholders(Path.cwd() / ".env-sample")
    replace_placeholders(Path.cwd() / ".azure-pipelines/pr-pipeline.yaml")
    replace_placeholders(Path.cwd() / ".azure-pipelines/jobs/test-suite.yaml")
    replace_placeholders(Path.cwd() / ".azure-pipelines/steps/uv-env-create.yaml")
    replace_placeholders(Path.cwd() / ".azure-pipelines/steps/test-suite.yaml")
    replace_placeholders(Path.cwd() / ".github/workflows/lock-files-update.yaml")
    replace_placeholders(Path.cwd() / ".github/workflows/zizmor-security-check.yaml")
    init_git_repo()
    configure_remote()


if __name__ == "__main__":
    main()
