from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from cookiecutter.main import cookiecutter

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from _pytest.tmpdir import TempPathFactory

MLPCC_ROOT = Path(__file__).parents[1].resolve()
DEFAULT_PROJECT_PARAMS = {
    "project_name": "dummy project",
    "src_dir_name": "dummy_project",
    "author_name": "Some Dummy Author",
    "license": "MIT",
    "python_version": "3.12",
}
COOKIECUTTER_CONFIG_FP = MLPCC_ROOT / "cookiecutter.json"
COOKIECUTTER_CONFIG = json.loads(COOKIECUTTER_CONFIG_FP.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def dummy_project_dir(tmp_path_factory: TempPathFactory) -> Generator[Path]:
    temp_dir = tmp_path_factory.mktemp("dummy-ml-project")
    out_dir = Path(temp_dir).resolve()
    cookiecutter(str(MLPCC_ROOT), no_input=True, output_dir=temp_dir, extra_context=DEFAULT_PROJECT_PARAMS)
    yield next(iter(out_dir.iterdir()))
    shutil.rmtree(out_dir)


@pytest.fixture
def dummy_project_factory(tmp_path_factory: TempPathFactory) -> Callable[[str], Path]:
    def _create_project(override_license: str) -> Path:
        temp_dir = tmp_path_factory.mktemp("dummy-ml-project")
        out_dir = Path(temp_dir).resolve()
        cookiecutter(
            str(MLPCC_ROOT),
            no_input=True,
            output_dir=temp_dir,
            extra_context={
                "project_name": "dummy project",
                "author_name": "Some Dummy Author",
                "license": override_license,
            },
        )
        return next(iter(out_dir.iterdir()))

    return _create_project
