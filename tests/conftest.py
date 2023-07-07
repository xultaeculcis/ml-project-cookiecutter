import shutil
from pathlib import Path
from typing import Callable, Generator

import pytest
from _pytest.tmpdir import TempPathFactory
from cookiecutter.main import cookiecutter

MLPCC_ROOT = Path(__file__).parents[1].resolve()
DEFAULT_PROJECT_PARAMS = {
    "project_name": "dummy project",
    "author_name": "Some Dummy Author",
    "license": "MIT",
}


@pytest.fixture(scope="module")
def dummy_project_dir(tmp_path_factory: TempPathFactory) -> Generator[Path, None, None]:
    temp_dir = tmp_path_factory.mktemp("dummy-ml-project")
    out_dir = Path(temp_dir).resolve()
    cookiecutter(str(MLPCC_ROOT), no_input=True, output_dir=temp_dir, extra_context=DEFAULT_PROJECT_PARAMS)
    yield list(out_dir.iterdir())[0]
    shutil.rmtree(out_dir)


@pytest.fixture()
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
        return list(out_dir.iterdir())[0]

    return _create_project
