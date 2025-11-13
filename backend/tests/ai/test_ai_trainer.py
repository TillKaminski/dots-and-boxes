"""Test Training Process and Metrics."""

from unittest.mock import MagicMock
from ai.training.trainer import ModelTrainer


def test_trainer_constructor():
    """Test Constructor."""
    trainer = ModelTrainer()
    assert isinstance(trainer, ModelTrainer)


def test_trainer_train_exists():
    """Test train-Method."""
    trainer = ModelTrainer()
    assert callable(trainer.train)


def test_trainer_train_is_called():
    """Mocks Training Process."""
    trainer = ModelTrainer()
    trainer.train = MagicMock(name="train_mock")
    trainer.train()
    trainer.train.assert_called_once()
