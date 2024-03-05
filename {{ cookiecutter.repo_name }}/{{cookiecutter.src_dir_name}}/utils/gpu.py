import os


def set_gpu_power_limit_if_needed(gpu_name: str = "NVIDIA GeForce RTX 3090", pw: int = 250) -> None:
    """
    Helper function, that sets GPU power limit if specified GPU is used.

    Args:
        gpu_name: The name of the GPU to assign the new power limit to. Default: "NVIDIA GeForce RTX 3090".
        pw: The new power limit to set. Defaults to 250W.

    """

    stream = os.popen("nvidia-smi --query-gpu=gpu_name --format=csv")
    gpu_list = stream.read()
    if gpu_name in gpu_list:
        os.system("sudo nvidia-smi -pm 1")
        os.system(f"sudo nvidia-smi -pl {pw}")
