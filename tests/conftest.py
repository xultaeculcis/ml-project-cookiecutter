from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from cookiecutter.main import cookiecutter

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from _pytest.tmpdir import TempPathFactory

    ProjectFactory = Callable[..., Path]

MLPCC_ROOT = Path(__file__).parents[1].resolve()
COOKIECUTTER_CONFIG_FP = MLPCC_ROOT / "cookiecutter.json"
COOKIECUTTER_CONFIG = json.loads(COOKIECUTTER_CONFIG_FP.read_text(encoding="utf-8"))
DEFAULT_PROJECT_PARAMS: dict[str, Any] = {
    "project_name": "dummy project",
    "author_name": "Some Dummy Author",
    "license": "MIT",
    "python_version": "3.12",
}
GIT_IDENTITY_ENV = {
    "GIT_AUTHOR_NAME": "Test Author",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test Author",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


def generate_project(output_dir: Path, **overrides: Any) -> Path:
    """Generate a project from the template and return its directory."""
    context = {**DEFAULT_PROJECT_PARAMS, **overrides}
    return Path(cookiecutter(str(MLPCC_ROOT), no_input=True, output_dir=str(output_dir), extra_context=context))


@pytest.fixture(scope="session", autouse=True)
def _isolated_cookiecutter_config(tmp_path_factory: TempPathFactory) -> Generator[None]:
    """Keep cookiecutter replay files and cloned templates out of the real home directory."""
    config_dir = tmp_path_factory.mktemp("cookiecutter-config")
    config_fp = config_dir / "config.yaml"
    config_fp.write_text(
        f"cookiecutters_dir: {(config_dir / 'cookiecutters').as_posix()}\n"
        f"replay_dir: {(config_dir / 'replay').as_posix()}\n",
        encoding="utf-8",
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("COOKIECUTTER_CONFIG", str(config_fp))
        yield


@pytest.fixture(autouse=True)
def _git_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in GIT_IDENTITY_ENV.items():
        monkeypatch.setenv(key, value)


@pytest.fixture(scope="module")
def dummy_project_dir(tmp_path_factory: TempPathFactory) -> Path:
    with pytest.MonkeyPatch.context() as mp:
        for key, value in GIT_IDENTITY_ENV.items():
            mp.setenv(key, value)
        return generate_project(tmp_path_factory.mktemp("dummy-ml-project"))


@pytest.fixture
def project_factory(tmp_path_factory: TempPathFactory) -> ProjectFactory:
    """Generate a project with any cookiecutter context overrides, e.g. `project_factory(ci_provider="none")`."""

    def _create_project(**overrides: Any) -> Path:
        return generate_project(tmp_path_factory.mktemp("dummy-ml-project"), **overrides)

    return _create_project
