"""PyTorch utils."""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import shutil
import subprocess

import torch

from {{cookiecutter.package_name}}.utils.logging import get_logger

_logger = get_logger(__name__)


def _is_available(device: torch.device) -> bool:
    if device.type == "cuda":
        return torch.cuda.is_available() and (device.index is None or device.index < torch.cuda.device_count())
    if device.type == "mps":
        return torch.backends.mps.is_available()
    # CPU and other device types: trust the caller.
    return True


def get_device(prefer: str | None = None) -> torch.device:
    """Return the device to run on.

    Args:
        prefer: The preferred device, for example `"cuda"`, `"cuda:1"`, `"mps"` or `"cpu"`. If it is not available,
            the function logs a warning and selects a device automatically.

    Returns:
        The preferred device if it is available. Otherwise the first available device of CUDA, MPS and CPU.

    """
    if prefer is not None:
        device = torch.device(prefer)
        if _is_available(device):
            return device
        _logger.warning("Device %s is not available. Selecting a device automatically.", prefer)

    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def set_gpu_power_limit_if_needed(gpu_name: str = "NVIDIA GeForce RTX 3090", power_limit: int = 250) -> bool:
    """Set the GPU power limit with `nvidia-smi` if a GPU with the given name is installed.

    Changing the power limit needs root. If `sudo` is on the `PATH`, the commands run with `sudo -n` (non-interactive):
    they fail instead of asking for a password. Configure passwordless sudo for `nvidia-smi` or run as root.

    Args:
        gpu_name: The GPU name, as `nvidia-smi --query-gpu=name` shows it.
        power_limit: The new power limit in watts.

    Returns:
        `True` if the power limit was set. `False` if `nvidia-smi` is missing, the GPU is not installed or a command
        failed.

    """
    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi is None:
        return False

    query = subprocess.run(  # noqa: S603
        [nvidia_smi, "--query-gpu=name", "--format=csv,noheader"],
        capture_output=True,
        text=True,
        check=False,
    )
    if query.returncode != 0 or gpu_name not in query.stdout.splitlines():
        return False

    sudo = shutil.which("sudo")
    prefix = [sudo, "-n"] if sudo is not None else []
    for args in (["-pm", "1"], ["-pl", str(power_limit)]):
        result = subprocess.run([*prefix, nvidia_smi, *args], capture_output=True, text=True, check=False)  # noqa: S603
        if result.returncode != 0:
            _logger.warning("nvidia-smi %s failed: %s", " ".join(args), result.stderr.strip())
            return False
    return True
