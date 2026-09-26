"""Check the LICENSE file and the license metadata in pyproject.toml for every license choice."""

from __future__ import annotations

import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.conftest import COOKIECUTTER_CONFIG

if TYPE_CHECKING:
    from tests.conftest import ProjectFactory

LICENSES_DIR = Path(__file__).parent / "licenses"
EMPTY_LICENSE = "Empty license file"
# Licenses with an SPDX identifier that must show up in the pyproject.toml metadata.
SPDX_IDS = {
    "MIT": "MIT",
    "Apache 2.0": "Apache-2.0",
    "BSD-3-Clause": "BSD-3-Clause",
}


def _license_metadata(pyproject_fp: Path) -> str:
    """Return the license field and the license classifiers of a pyproject.toml as one string."""
    project = tomllib.loads(pyproject_fp.read_text(encoding="utf-8"))["project"]
    license_field = project.get("license", "")
    if isinstance(license_field, dict):
        license_field = " ".join(str(value) for value in license_field.values())
    classifiers = [c for c in project.get("classifiers", []) if c.startswith("License ::")]
    return " | ".join([str(license_field), *classifiers])


@pytest.mark.parametrize("license_type", COOKIECUTTER_CONFIG["license"])
def test_license_file(project_factory: ProjectFactory, license_type: str) -> None:
    project_dir = project_factory(license=license_type)
    content = (project_dir / "LICENSE").read_text(encoding="utf-8")
    if license_type == EMPTY_LICENSE:
        assert content == ""
        return
    expected = (LICENSES_DIR / f"{license_type}.txt").read_text(encoding="utf-8")
    expected = expected.format(year=datetime.now(tz=UTC).year)
    assert expected.strip() in content
    assert "{{" not in content
    assert "{%" not in content


def test_every_license_choice_has_expected_text() -> None:
    expected_files = {fp.stem for fp in LICENSES_DIR.glob("*.txt")}
    assert expected_files == set(COOKIECUTTER_CONFIG["license"])


@pytest.mark.parametrize("license_type", COOKIECUTTER_CONFIG["license"])
def test_pyproject_license_metadata(project_factory: ProjectFactory, license_type: str) -> None:
    """B2: pyproject.toml must not claim MIT for other licenses, and must name the chosen SPDX license."""
    project_dir = project_factory(license=license_type)
    metadata = _license_metadata(project_dir / "pyproject.toml")
    if license_type != "MIT":
        assert "MIT" not in metadata
    if license_type in SPDX_IDS:
        assert SPDX_IDS[license_type] in metadata
