"""Check that each cookiecutter option adds or removes the expected files."""

from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING, Any

import pytest

from tests.conftest import COOKIECUTTER_CONFIG
from tests.helpers import is_ci_file, project_text_files, unrendered_jinja_markers

if TYPE_CHECKING:
    from tests.conftest import ProjectFactory

PACKAGE = "dummy_project"

GITHUB_PR_FILES = [".github/workflows/pr.yaml", ".github/workflows/nightly.yaml"]
AZURE_FILES = [".azure-pipelines"]
DEPENDABOT_FILES = [".github/dependabot.yaml"]
LOCK_UPDATE_FILES = [".github/workflows/lock-files-update.yaml"]
ZIZMOR_WORKFLOW_FILES = [".github/workflows/zizmor-security-check.yaml"]
DOCKER_FILES = ["Dockerfile", ".dockerignore", "mk/docker.mk"]
AZURE_ML_FILES = ["aml", "mk/aml.mk", ".amlignore", "docs/guides/azure-ml.md"]
AGENT_DOCS_FILES = ["CLAUDE.md", "CONTEXT.md", "docs/glossary.md", "docs/adr"]
TORCH_FILES = [f"src/{PACKAGE}/utils/torch.py", "tests/unit/utils/test_torch.py"]
LIGHTNING_FILES = [f"src/{PACKAGE}/lightning", "tests/unit/lightning", "configs/lightning", "docs/api_ref/lightning.md"]

# (overrides, paths that must exist, paths that must not exist)
OPTION_CASES: list[tuple[dict[str, str], list[str], list[str]]] = [
    ({"ci_provider": "github"}, GITHUB_PR_FILES, AZURE_FILES),
    ({"ci_provider": "azure"}, AZURE_FILES, GITHUB_PR_FILES),
    ({"ci_provider": "none"}, [], GITHUB_PR_FILES + AZURE_FILES),
    ({"dependabot": "yes"}, DEPENDABOT_FILES, []),
    ({"dependabot": "no"}, [], DEPENDABOT_FILES),
    ({"lock_update_workflow": "yes"}, LOCK_UPDATE_FILES, []),
    ({"lock_update_workflow": "no"}, [], LOCK_UPDATE_FILES),
    ({"zizmor": "workflow-sarif"}, ZIZMOR_WORKFLOW_FILES, []),
    ({"zizmor": "pre-commit"}, [], ZIZMOR_WORKFLOW_FILES),
    ({"zizmor": "no"}, [], ZIZMOR_WORKFLOW_FILES),
    ({"docker": "yes"}, DOCKER_FILES, []),
    ({"docker": "no"}, [], DOCKER_FILES),
    ({"azure_ml": "yes"}, AZURE_ML_FILES, []),
    ({"azure_ml": "no"}, [], AZURE_ML_FILES),
    ({"agent_docs": "yes"}, AGENT_DOCS_FILES, []),
    ({"agent_docs": "no"}, [], AGENT_DOCS_FILES),
    ({"ml_stack": "sklearn"}, [], TORCH_FILES + LIGHTNING_FILES),
    ({"ml_stack": "none"}, [], TORCH_FILES + LIGHTNING_FILES),
    ({"ml_stack": "torch"}, TORCH_FILES, LIGHTNING_FILES),
    ({"ml_stack": "lightning"}, TORCH_FILES + LIGHTNING_FILES, []),
    (
        {"ci_provider": "none", "dependabot": "no", "lock_update_workflow": "no", "zizmor": "no"},
        [],
        [".github"],
    ),
    (
        {"ci_provider": "azure", "dependabot": "no", "lock_update_workflow": "no", "zizmor": "pre-commit"},
        AZURE_FILES,
        [".github"],
    ),
]

ML_STACK_DEPENDENCIES: dict[str, tuple[set[str], set[str]]] = {
    # ml_stack: (required dependency names, forbidden dependency names)
    "sklearn": ({"scikit-learn"}, {"torch", "lightning"}),
    "torch": ({"torch"}, {"scikit-learn", "lightning"}),
    "lightning": ({"torch", "lightning"}, {"scikit-learn"}),
    "none": (set(), {"torch", "lightning", "scikit-learn"}),
}


def _case_id(case: dict[str, str]) -> str:
    return ",".join(f"{key}={value}" for key, value in case.items())


def _dependency_names(pyproject: dict[str, Any]) -> set[str]:
    names = set()
    for requirement in pyproject["project"]["dependencies"]:
        name = requirement.split(";")[0]
        for separator in ("[", "=", ">", "<", "~", "!", " "):
            name = name.split(separator)[0]
        names.add(name.strip().lower())
    return names


@pytest.mark.parametrize(
    ("overrides", "present", "absent"), OPTION_CASES, ids=[_case_id(case[0]) for case in OPTION_CASES]
)
def test_option_files(
    project_factory: ProjectFactory, overrides: dict[str, str], present: list[str], absent: list[str]
) -> None:
    project_dir = project_factory(**overrides)
    missing = [rel_path for rel_path in present if not (project_dir / rel_path).exists()]
    unexpected = [rel_path for rel_path in absent if (project_dir / rel_path).exists()]
    assert missing == []
    assert unexpected == []

    offenders = {
        fp.relative_to(project_dir).as_posix(): markers
        for fp, content in project_text_files(project_dir).items()
        if (markers := unrendered_jinja_markers(content, allow_ci_expressions=is_ci_file(project_dir, fp)))
    }
    assert offenders == {}


@pytest.mark.parametrize("zizmor", COOKIECUTTER_CONFIG["zizmor"])
def test_zizmor_pre_commit_hook(project_factory: ProjectFactory, zizmor: str) -> None:
    project_dir = project_factory(zizmor=zizmor)
    pre_commit_config = (project_dir / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert ("zizmor" in pre_commit_config) is (zizmor == "pre-commit")


@pytest.mark.parametrize("ml_stack", COOKIECUTTER_CONFIG["ml_stack"])
def test_ml_stack_dependencies(project_factory: ProjectFactory, ml_stack: str) -> None:
    project_dir = project_factory(ml_stack=ml_stack)
    pyproject = tomllib.loads((project_dir / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = _dependency_names(pyproject)
    required, forbidden = ML_STACK_DEPENDENCIES[ml_stack]
    assert required <= dependencies
    assert forbidden.isdisjoint(dependencies)


@pytest.mark.parametrize("python_version", COOKIECUTTER_CONFIG["python_version"])
def test_python_version(project_factory: ProjectFactory, python_version: str) -> None:
    """B5: the chosen Python version must be used by uv (.python-version) and by the tools."""
    project_dir = project_factory(python_version=python_version)
    assert (project_dir / ".python-version").read_text(encoding="utf-8").strip() == python_version

    pyproject = tomllib.loads((project_dir / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["requires-python"] in {f">={python_version}", f">={python_version}.0"}
    assert pyproject["tool"]["ruff"]["target-version"] == f"py{python_version.replace('.', '')}"


@pytest.mark.parametrize("python_version", COOKIECUTTER_CONFIG["python_version"])
def test_future_annotations_import(project_factory: ProjectFactory, python_version: str) -> None:
    """Python 3.14 does not need `from __future__ import annotations` (PEP 649). Older versions require it."""
    project_dir = project_factory(python_version=python_version)
    content = (project_dir / "src" / PACKAGE / "core" / "settings.py").read_text(encoding="utf-8")
    assert ("from __future__ import annotations" in content) is (python_version != "3.14")
