"""Tests for the pre- and post-generation hooks."""

from __future__ import annotations

import sys
import tomllib
from typing import TYPE_CHECKING

import pytest
import yaml
from cookiecutter.exceptions import FailedHookException

from hooks import post_gen_project, pre_gen_project
from tests.conftest import GIT_IDENTITY_ENV
from tests.helpers import git

if TYPE_CHECKING:
    from pathlib import Path

    from tests.conftest import ProjectFactory


@pytest.mark.parametrize(
    "overrides",
    [
        {"package_name": "1package"},
        {"package_name": "my-package"},
        {"package_name": "class"},
        {"package_name": "match"},
        {"package_name": "my package"},
        {"repo_name": "Bad_Name"},
        {"repo_name": "-leading-hyphen"},
        {"repo_name": "has space"},
    ],
    ids=lambda overrides: next(iter(overrides.values())),
)
def test_pre_gen_rejects_invalid_names(project_factory: ProjectFactory, overrides: dict[str, str]) -> None:
    with pytest.raises(FailedHookException):
        project_factory(**overrides)


# A context with every option off, so the post-gen hook removes as much as it can.
MINIMAL_CONTEXT = {
    "package_name": "pkg",
    "ci_provider": "none",
    "dependabot": "no",
    "lock_update_workflow": "no",
    "zizmor": "no",
    "docker": "no",
    "azure_ml": "no",
    "agent_docs": "no",
    "ml_stack": "none",
}


@pytest.mark.parametrize(
    ("package_name", "repo_name"),
    [("pkg", "repo"), ("my_pkg2", "my-repo-2"), ("_private", "0repo")],
)
def test_pre_gen_validate_accepts_valid_names(package_name: str, repo_name: str) -> None:
    assert pre_gen_project.validate(package_name=package_name, repo_name=repo_name) == []


@pytest.mark.parametrize(
    "package_name",
    [
        "mlflow",
        "torch",
        "lightning",
        "click",
        "numpy",
        "pandas",
        "pydantic",
        "pydantic_settings",
        "yaml",
        "tqdm",
        "psutil",
        "pyarrow",
        "sklearn",
        "jsonargparse",
        "dotenv",
        "logging",
        "json",
        "random",
    ],
)
def test_pre_gen_rejects_shadowing_package_names(package_name: str) -> None:
    errors = pre_gen_project.validate(package_name=package_name, repo_name="repo")
    assert any("standard library module or of a dependency" in error for error in errors)


def test_pre_gen_rejects_all_stdlib_module_names() -> None:
    for name in sorted(sys.stdlib_module_names):
        if name.isidentifier():
            assert pre_gen_project.validate(package_name=name, repo_name="repo"), name


def test_shadowed_package_name_fails_generation(project_factory: ProjectFactory) -> None:
    with pytest.raises(FailedHookException):
        project_factory(project_name="mlflow")


@pytest.mark.parametrize(
    "github_username",
    ["", "-leading", "has space", "a" * 40, "under_score", 'quote"', "o'brien"],
)
def test_pre_gen_rejects_invalid_github_username(github_username: str) -> None:
    errors = pre_gen_project.validate(package_name="pkg", repo_name="repo", github_username=github_username)
    assert any("github_username" in error for error in errors)


@pytest.mark.parametrize("github_username", ["a", "Some-Org", "user123", "a" * 39])
def test_pre_gen_accepts_valid_github_username(github_username: str) -> None:
    assert pre_gen_project.validate(package_name="pkg", repo_name="repo", github_username=github_username) == []


@pytest.mark.parametrize("value", ['Predict "churn"', "back\\slash", "two\nlines"])
@pytest.mark.parametrize("key", pre_gen_project.FREE_TEXT_KEYS)
def test_pre_gen_rejects_unsafe_free_text(key: str, value: str) -> None:
    errors = pre_gen_project.validate(package_name="pkg", repo_name="repo", texts={key: value})
    assert len(errors) == 1
    assert key in errors[0]


@pytest.mark.parametrize(
    "overrides",
    [
        {"project_description": 'Predict "churn": v2'},
        {"author_name": 'The "A" Team'},
        {"project_name": "back\\slash"},
    ],
    ids=["description-quote", "author-quote", "name-backslash"],
)
def test_unsafe_free_text_fails_generation(project_factory: ProjectFactory, overrides: dict[str, str]) -> None:
    with pytest.raises(FailedHookException):
        project_factory(**overrides)


def test_description_with_colon_and_apostrophe_renders_valid_files(project_factory: ProjectFactory) -> None:
    """Free text with YAML/TOML special characters must not break the generated config files."""
    description = "Predict churn: v2 - the customer's #1 model"
    author = "Bob O'Brien & Co: {Team}"
    project_dir = project_factory(project_description=description, author_name=author, docker="yes")

    pyproject = tomllib.loads((project_dir / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["description"] == description
    assert pyproject["project"]["authors"] == [{"name": author}]
    mkdocs = yaml.load((project_dir / "mkdocs.yml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader)  # noqa: S506
    assert mkdocs["site_description"] == description
    assert author in mkdocs["copyright"]
    assert f'org.opencontainers.image.description="{description}"' in (project_dir / "Dockerfile").read_text(
        encoding="utf-8"
    )


def test_author_with_apostrophe_gives_valid_github_username(project_factory: ProjectFactory) -> None:
    project_dir = project_factory(author_name="Bob O'Brien")
    proc = git(project_dir, "remote", "get-url", "origin")
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "https://github.com/bob-o-brien/dummy-project"


def test_post_gen_removal_tolerates_missing_paths(tmp_path: Path) -> None:
    """The removal table must not fail when a path was never created."""
    post_gen_project.remove_disabled_features(tmp_path, MINIMAL_CONTEXT)
    assert list(tmp_path.iterdir()) == []


def test_post_gen_prunes_empty_github_dir(tmp_path: Path) -> None:
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    post_gen_project.remove_disabled_features(tmp_path, MINIMAL_CONTEXT)
    assert not (tmp_path / ".github").exists()


def test_post_gen_keeps_non_empty_github_dir(tmp_path: Path) -> None:
    workflow = tmp_path / ".github" / "workflows" / "custom.yaml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("name: custom\n", encoding="utf-8")
    post_gen_project.remove_disabled_features(tmp_path, MINIMAL_CONTEXT)
    assert workflow.exists()


def test_custom_repo_url_is_used_for_origin(project_factory: ProjectFactory) -> None:
    """B3: the remote must be the repo_url value, not something built from package_name."""
    repo_url = "git@example.com:team/custom-repo.git"
    project_dir = project_factory(repo_url=repo_url)
    proc = git(project_dir, "remote", "get-url", "origin")
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == repo_url


def test_generation_without_git_identity(
    project_factory: ProjectFactory, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """B4: a missing git identity must not make cookiecutter fail and delete the project."""
    for key in [*GIT_IDENTITY_ENV, "EMAIL"]:
        monkeypatch.delenv(key, raising=False)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")

    project_dir = project_factory()

    assert (project_dir / "pyproject.toml").is_file()
    assert (project_dir / ".git").is_dir()
    proc = git(project_dir, "branch", "--show-current")
    assert proc.stdout.strip() == "main"


def test_generation_without_git(
    project_factory: ProjectFactory, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Missing git must not make cookiecutter fail."""
    empty_bin = tmp_path / "bin"
    empty_bin.mkdir()
    monkeypatch.setenv("PATH", str(empty_bin))

    project_dir = project_factory()

    assert (project_dir / "pyproject.toml").is_file()
    assert not (project_dir / ".git").exists()
