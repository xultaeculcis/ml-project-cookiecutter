"""Tests for the uv version sync in `.github/scripts/update_template_deps.py`."""

from __future__ import annotations

import importlib.util
import re
import sys
from typing import TYPE_CHECKING

import pytest

from tests.conftest import MLPCC_ROOT

if TYPE_CHECKING:
    from types import ModuleType

SCRIPT_FP = MLPCC_ROOT / ".github" / "scripts" / "update_template_deps.py"
TEMPLATE_DIR = MLPCC_ROOT / "{{ cookiecutter.repo_name }}"


@pytest.fixture(scope="module")
def script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("update_template_deps", SCRIPT_FP)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


DOCKERFILE = """# syntax=docker/dockerfile:1
ARG PYTHON_VERSION={{cookiecutter.python_version}}
FROM ghcr.io/astral-sh/uv:0.12.19 AS uv
FROM python:{{cookiecutter.python_version}}-slim-trixie AS builder
# image: ghcr.io/astral-sh/uv:python{{cookiecutter.python_version}}-trixie-slim
"""

AZURE_STEP = """parameters:
  # Pinned uv version. Update it together with the uv version used locally.
  - name: uvVersion
    type: string
    default: "0.12.19"
  - name: other
    type: string
    default: "keep-me"

steps:
  - bash: echo "{% raw %}${{ parameters.uvVersion }}{% endraw %}"
"""


@pytest.mark.parametrize("version", ["0.13.0", "v0.13.0"])
def test_set_dockerfile_uv_version(script: ModuleType, version: str) -> None:
    result = script.set_dockerfile_uv_version(DOCKERFILE, version)
    assert "FROM ghcr.io/astral-sh/uv:0.13.0 AS uv" in result
    # Jinja and the uv image tags that are not a version stay as they are.
    assert result == DOCKERFILE.replace("uv:0.12.19", "uv:0.13.0")


@pytest.mark.parametrize("version", ["0.13.0", "v0.13.0"])
def test_set_azure_uv_version(script: ModuleType, version: str) -> None:
    result = script.set_azure_uv_version(AZURE_STEP, version)
    assert result == AZURE_STEP.replace('default: "0.12.19"', 'default: "0.13.0"')
    assert 'default: "keep-me"' in result


def test_patterns_match_the_template_files(script: ModuleType) -> None:
    """The regexes must find the pins in the real template files, or the sync does nothing."""
    dockerfile = (TEMPLATE_DIR / script.DOCKERFILE).read_text(encoding="utf-8")
    azure_step = (TEMPLATE_DIR / script.AZURE_UV_STEP).read_text(encoding="utf-8")
    assert len(script.DOCKERFILE_UV_PATTERN.findall(dockerfile)) == 1
    assert len(script.AZURE_UV_PATTERN.findall(azure_step)) == 1


def test_uv_pins_are_in_sync(script: ModuleType) -> None:
    """The Dockerfile and Azure Pipelines uv versions must equal the `uv-pre-commit` rev."""
    pre_commit = (TEMPLATE_DIR / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    rev = re.search(r"astral-sh/uv-pre-commit\s*\n\s+rev:\s+v?(\S+)", pre_commit)
    assert rev is not None
    dockerfile = (TEMPLATE_DIR / script.DOCKERFILE).read_text(encoding="utf-8")
    azure_step = (TEMPLATE_DIR / script.AZURE_UV_STEP).read_text(encoding="utf-8")
    assert script.set_dockerfile_uv_version(dockerfile, rev.group(1)) == dockerfile
    assert script.set_azure_uv_version(azure_step, rev.group(1)) == azure_step
