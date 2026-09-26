{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import pytest_socket

from {{cookiecutter.package_name}}.core.settings import get_settings

if TYPE_CHECKING:
    from collections.abc import Iterator

# MLflow telemetry makes network calls, which pytest-socket blocks in unit tests.
os.environ.setdefault("MLFLOW_DISABLE_TELEMETRY", "true")

TESTS_DIR = Path(__file__).parent
SUITE_MARKERS = ("unit", "integration", "e2e")
# MLflow environment variables that a shell or an earlier test can set. Tests that need them set them with monkeypatch.
MLFLOW_ENV_VARS = ("MLFLOW_EXPERIMENT_NAME", "MLFLOW_TRACKING_URI", "MLFLOW_RUN_ID")


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark each test with the name of its suite directory: `tests/<suite>/...`."""
    for item in items:
        try:
            suite = item.path.relative_to(TESTS_DIR).parts[0]
        except ValueError:
            continue
        if suite in SUITE_MARKERS:
            item.add_marker(getattr(pytest.mark, suite))


@pytest.fixture(autouse=True)
def _block_network_in_unit_tests(request: pytest.FixtureRequest) -> Iterator[None]:
    """Unit tests must not use the network. Unix sockets stay allowed for local IPC."""
    if request.node.get_closest_marker("unit") is None:
        yield
        return
    pytest_socket.disable_socket(allow_unix_socket=True)
    try:
        yield
    finally:
        pytest_socket.enable_socket()


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    """Build the settings again in each test, so environment changes in one test do not leak into the next."""
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _clean_mlflow_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove the MLflow environment variables, so a run or an experiment never leaks from one test into the next."""
    for name in MLFLOW_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
