"""Example LightningModule: linear regression. Replace it with your model."""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import torch
from lightning.pytorch import LightningModule
from torch import nn


class LinearRegressionModule(LightningModule):
    """Linear regression trained with mean squared error."""

    def __init__(self, in_features: int = 8, learning_rate: float = 1e-2) -> None:
        """Create the model.

        Args:
            in_features: Number of input features.
            learning_rate: Learning rate of the Adam optimizer.

        """
        super().__init__()
        self.save_hyperparameters()
        self.learning_rate = learning_rate
        self.model = nn.Linear(in_features, 1)
        self.loss_fn = nn.MSELoss()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Run the model.

        Args:
            x: Input tensor with shape `(batch, in_features)`.

        Returns:
            Predictions with shape `(batch,)`.

        """
        return self.model(x).squeeze(-1)  # type: ignore[no-any-return]

    def _step(self, batch: tuple[torch.Tensor, torch.Tensor], stage: str) -> torch.Tensor:
        x, y = batch
        loss: torch.Tensor = self.loss_fn(self(x), y)
        self.log(f"{stage}/loss", loss, prog_bar=True)
        return loss

    def training_step(self, batch: tuple[torch.Tensor, torch.Tensor], batch_idx: int) -> torch.Tensor:  # noqa: ARG002
        """Run one training step."""
        return self._step(batch, "train")

    def validation_step(self, batch: tuple[torch.Tensor, torch.Tensor], batch_idx: int) -> torch.Tensor:  # noqa: ARG002
        """Run one validation step."""
        return self._step(batch, "val")

    def test_step(self, batch: tuple[torch.Tensor, torch.Tensor], batch_idx: int) -> torch.Tensor:  # noqa: ARG002
        """Run one test step."""
        return self._step(batch, "test")

    def predict_step(self, batch: tuple[torch.Tensor, torch.Tensor], batch_idx: int) -> torch.Tensor:  # noqa: ARG002
        """Return the predictions for one batch."""
        x, _ = batch
        return self(x)  # type: ignore[no-any-return]

    def configure_optimizers(self) -> torch.optim.Optimizer:
        """Create the optimizer."""
        return torch.optim.Adam(self.parameters(), lr=self.learning_rate)
