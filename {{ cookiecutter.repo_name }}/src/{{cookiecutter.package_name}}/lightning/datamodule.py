"""Example LightningDataModule with random regression data. Replace it with your data."""

{% if cookiecutter.python_version != "3.14" -%}
from __future__ import annotations

{% endif -%}
import torch
from lightning.pytorch import LightningDataModule
from torch.utils.data import DataLoader, Dataset, TensorDataset, random_split

_Batch = tuple[torch.Tensor, ...]


class RandomRegressionDataModule(LightningDataModule):
    """Random data for a linear regression: `y = x @ w + noise`."""

    def __init__(self, num_samples: int = 256, in_features: int = 8, batch_size: int = 32, seed: int = 42) -> None:
        """Create the data module.

        Args:
            num_samples: Total number of samples. 80% are for training, 10% for validation and 10% for testing.
            in_features: Number of input features.
            batch_size: Batch size.
            seed: Seed of the data generator.

        """
        super().__init__()
        self.save_hyperparameters()
        self.num_samples = num_samples
        self.in_features = in_features
        self.batch_size = batch_size
        self.seed = seed
        self.train_ds: Dataset[_Batch] | None = None
        self.val_ds: Dataset[_Batch] | None = None
        self.test_ds: Dataset[_Batch] | None = None

    def setup(self, stage: str) -> None:  # noqa: ARG002
        """Generate the data and split it."""
        generator = torch.Generator().manual_seed(self.seed)
        x = torch.randn(self.num_samples, self.in_features, generator=generator)
        weights = torch.randn(self.in_features, generator=generator)
        y = x @ weights + 0.1 * torch.randn(self.num_samples, generator=generator)
        n_val = n_test = self.num_samples // 10
        n_train = self.num_samples - n_val - n_test
        train, val, test = random_split(TensorDataset(x, y), [n_train, n_val, n_test], generator=generator)
        self.train_ds, self.val_ds, self.test_ds = train, val, test

    def train_dataloader(self) -> DataLoader[_Batch]:
        """Return the training data loader."""
        return DataLoader(self._require(self.train_ds), batch_size=self.batch_size, shuffle=True)

    def val_dataloader(self) -> DataLoader[_Batch]:
        """Return the validation data loader."""
        return DataLoader(self._require(self.val_ds), batch_size=self.batch_size)

    def test_dataloader(self) -> DataLoader[_Batch]:
        """Return the test data loader."""
        return DataLoader(self._require(self.test_ds), batch_size=self.batch_size)

    def predict_dataloader(self) -> DataLoader[_Batch]:
        """Return the prediction data loader (the test split)."""
        return self.test_dataloader()

    @staticmethod
    def _require(dataset: Dataset[_Batch] | None) -> Dataset[_Batch]:
        if dataset is None:
            msg = "Call setup() before you request a data loader."
            raise RuntimeError(msg)
        return dataset
