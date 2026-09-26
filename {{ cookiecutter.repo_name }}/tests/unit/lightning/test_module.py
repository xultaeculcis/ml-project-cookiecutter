{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import pytest
import torch

from {{cookiecutter.package_name}}.lightning.datamodule import RandomRegressionDataModule
from {{cookiecutter.package_name}}.lightning.module import LinearRegressionModule


def test_forward_shape() -> None:
    module = LinearRegressionModule(in_features=4)
    assert module(torch.randn(5, 4)).shape == (5,)


def test_training_step_returns_scalar_loss() -> None:
    module = LinearRegressionModule(in_features=4)
    loss = module.training_step((torch.randn(5, 4), torch.randn(5)), batch_idx=0)
    assert loss.ndim == 0
    assert loss.requires_grad


def test_configure_optimizers_uses_learning_rate() -> None:
    optimizer = LinearRegressionModule(learning_rate=0.5).configure_optimizers()
    assert optimizer.param_groups[0]["lr"] == 0.5


def test_datamodule_splits_and_batches() -> None:
    dm = RandomRegressionDataModule(num_samples=100, in_features=3, batch_size=16)
    dm.setup("fit")
    x, y = next(iter(dm.train_dataloader()))
    assert x.shape == (16, 3)
    assert y.shape == (16,)
    sizes = [len(loader.dataset) for loader in (dm.train_dataloader(), dm.val_dataloader(), dm.test_dataloader())]  # type: ignore[arg-type]
    assert sizes == [80, 10, 10]


def test_datamodule_is_deterministic() -> None:
    first, second = RandomRegressionDataModule(seed=1), RandomRegressionDataModule(seed=1)
    first.setup("fit")
    second.setup("fit")
    x1, _ = next(iter(first.test_dataloader()))
    x2, _ = next(iter(second.test_dataloader()))
    assert torch.equal(x1, x2)


def test_datamodule_requires_setup() -> None:
    with pytest.raises(RuntimeError, match="setup"):
        RandomRegressionDataModule().train_dataloader()
