{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import subprocess
from unittest.mock import MagicMock

import pytest
import torch

from {{cookiecutter.package_name}}.utils import torch as torch_utils
from {{cookiecutter.package_name}}.utils.torch import get_device, set_gpu_power_limit_if_needed

_NVIDIA_SMI = "/opt/bin/nvidia-smi"
_SUDO = "/opt/bin/sudo"


@pytest.fixture
def no_accelerators(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: False)


@pytest.fixture
def one_cuda_device(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(torch.cuda, "device_count", lambda: 1)


@pytest.mark.usefixtures("no_accelerators")
def test_get_device_falls_back_to_cpu() -> None:
    assert get_device() == torch.device("cpu")


@pytest.mark.usefixtures("no_accelerators")
def test_get_device_warns_when_preferred_device_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    warning = MagicMock()
    monkeypatch.setattr(torch_utils._logger, "warning", warning)  # noqa: SLF001
    assert get_device("cuda") == torch.device("cpu")
    warning.assert_called_once()


@pytest.mark.usefixtures("one_cuda_device")
def test_get_device_prefers_cuda_automatically() -> None:
    assert get_device() == torch.device("cuda")


@pytest.mark.usefixtures("one_cuda_device")
def test_get_device_returns_preferred_device() -> None:
    assert get_device("cpu") == torch.device("cpu")
    assert get_device("cuda:0") == torch.device("cuda:0")


@pytest.mark.usefixtures("one_cuda_device")
def test_get_device_rejects_cuda_index_out_of_range() -> None:
    assert get_device("cuda:1") == torch.device("cuda")


def test_get_device_uses_mps_when_cuda_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: True)
    assert get_device() == torch.device("mps")


def _completed(returncode: int = 0, stdout: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr="")


@pytest.fixture
def run_mock(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock(return_value=_completed(stdout="NVIDIA GeForce RTX 3090\n"))
    monkeypatch.setattr(torch_utils.subprocess, "run", mock)
    return mock


def _which(*available: str) -> object:
    paths = {"nvidia-smi": _NVIDIA_SMI, "sudo": _SUDO}
    return lambda name: paths[name] if name in available else None


def test_power_limit_without_nvidia_smi(monkeypatch: pytest.MonkeyPatch, run_mock: MagicMock) -> None:
    monkeypatch.setattr(torch_utils.shutil, "which", _which())
    assert set_gpu_power_limit_if_needed() is False
    run_mock.assert_not_called()


def test_power_limit_other_gpu(monkeypatch: pytest.MonkeyPatch, run_mock: MagicMock) -> None:
    monkeypatch.setattr(torch_utils.shutil, "which", _which("nvidia-smi", "sudo"))
    run_mock.return_value = _completed(stdout="AMD Radeon RX 6900 XT\n")
    assert set_gpu_power_limit_if_needed() is False
    assert run_mock.call_count == 1


def test_power_limit_uses_sudo_when_available(monkeypatch: pytest.MonkeyPatch, run_mock: MagicMock) -> None:
    monkeypatch.setattr(torch_utils.shutil, "which", _which("nvidia-smi", "sudo"))
    assert set_gpu_power_limit_if_needed(power_limit=280) is True
    commands = [c.args[0] for c in run_mock.call_args_list[1:]]
    assert commands == [
        [_SUDO, "-n", _NVIDIA_SMI, "-pm", "1"],
        [_SUDO, "-n", _NVIDIA_SMI, "-pl", "280"],
    ]


def test_power_limit_without_sudo(monkeypatch: pytest.MonkeyPatch, run_mock: MagicMock) -> None:
    monkeypatch.setattr(torch_utils.shutil, "which", _which("nvidia-smi"))
    assert set_gpu_power_limit_if_needed(gpu_name="NVIDIA GeForce RTX 3090", power_limit=250) is True
    assert run_mock.call_args_list[-1].args[0] == [_NVIDIA_SMI, "-pl", "250"]


def test_power_limit_command_failure(monkeypatch: pytest.MonkeyPatch, run_mock: MagicMock) -> None:
    monkeypatch.setattr(torch_utils.shutil, "which", _which("nvidia-smi", "sudo"))
    run_mock.side_effect = [_completed(stdout="NVIDIA GeForce RTX 3090\n"), _completed(returncode=1)]
    assert set_gpu_power_limit_if_needed() is False
    assert run_mock.call_count == 2
