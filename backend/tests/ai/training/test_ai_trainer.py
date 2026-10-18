"""Test Training Process and Metrics."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import torch
import torch.nn as nn

from torch.utils.data import DataLoader, TensorDataset
from backend.ai.training.trainer import ModelTrainer

MOCK_INPUT_SIZE = 10
MOCK_OUTPUT_SIZE = 4
MOCK_BATCH_SIZE = 2
MOCK_DROPOUT_RATE = 0.0

NUM_SAMPLES = 20

# Create Dataset for Mocking to prevent loading the whole Training Data
dummy_x = torch.randn(NUM_SAMPLES, MOCK_INPUT_SIZE)
dummy_y = torch.zeros(NUM_SAMPLES, MOCK_OUTPUT_SIZE)

for i in range(NUM_SAMPLES):
    dummy_y[i, i % MOCK_OUTPUT_SIZE] = 1.0

MOCK_DATA = [(dummy_x[i], dummy_y[i]) for i in range(NUM_SAMPLES)]


@pytest.fixture
def trainer_mock():
    """Simulates a Trainer Instance for each Test."""
    with patch("backend.ai.training.trainer.TrainingConfig") as MockTrainingConfig:
        with patch("backend.ai.training.trainer.ModelConfig") as MockModelConfig:
            with patch("torch.load", return_value=MOCK_DATA):

                MockTrainingConfig.BATCH_SIZE = MOCK_BATCH_SIZE
                MockTrainingConfig.LR_SCHEDULING = False
                MockTrainingConfig.NUM_EPOCHS = 1
                MockTrainingConfig.LEARNING_RATE = 0.001

                MockModelConfig.INPUT_SIZE = MOCK_INPUT_SIZE
                MockModelConfig.OUTPUT_SIZE = MOCK_OUTPUT_SIZE
                MockModelConfig.HIDDEN_LAYERS = [5]
                MockModelConfig.DROPOUT_RATE = MOCK_DROPOUT_RATE

                trainer = ModelTrainer()
                return trainer


@patch("torch.load", return_value=MOCK_DATA)
def test_trainer_constructor(MockLoad):
    """Test Constructor."""
    trainer = ModelTrainer()
    assert isinstance(trainer, ModelTrainer)


def test_trainer_constructor_setup(trainer_mock):
    """Test Trainer Initialization."""
    trainer = trainer_mock

    # Data Split (80% Training / 20% Validation)
    assert len(trainer.x_train) == 16
    assert len(trainer.x_val) == 4

    # DataLoader (Batch Size = 2)
    assert len(trainer.train_loader) == 16 / MOCK_BATCH_SIZE
    assert len(trainer.val_loader) == 4 / MOCK_BATCH_SIZE

    assert isinstance(trainer.model, torch.nn.Module)
    assert isinstance(trainer.criterion, nn.CrossEntropyLoss)
    assert isinstance(trainer.optimizer, torch.optim.Adam)
    # Scheduler disabled in Mock Configuration
    assert trainer.scheduler is None


def test_calculate_accuracy(trainer_mock):
    """Tests Precision of the Calculation."""
    trainer = trainer_mock

    # Create Feature- and Label-Vector
    x = torch.randn(4, MOCK_INPUT_SIZE)
    y = torch.tensor([0, 1, 0, 1], dtype=torch.long)

    test_loader = DataLoader(TensorDataset(x, y), batch_size=2)

    # Batch 1 Output (Sample 1 -> Label 0, Sample 2 -> Label -> 1)
    output_batch1 = torch.zeros(2, MOCK_OUTPUT_SIZE)
    output_batch1[0, 0] = 10.0
    output_batch1[1, 1] = 10.0

    # Batch 2 Output
    output_batch2 = torch.zeros(2, MOCK_OUTPUT_SIZE)
    output_batch2[0, 0] = 10.0
    output_batch2[1, 1] = 10.0

    with patch.object(
        trainer.model, "forward", side_effect=[output_batch1, output_batch2]
    ):
        accuracy = trainer.calculate_accuracy(test_loader)
        # all correct
        assert np.isclose(accuracy, 100.0)

    # first correct (S1 -> L0, S2 -> L0)
    output_batch1_bad = torch.zeros(2, MOCK_OUTPUT_SIZE)
    output_batch1_bad[:, 0] = 10.0

    # second correct
    output_batch2_bad = torch.zeros(2, MOCK_OUTPUT_SIZE)
    output_batch2_bad[:, 1] = 10.0

    with patch.object(
        trainer.model, "forward", side_effect=[output_batch1_bad, output_batch2_bad]
    ):
        accuracy = trainer.calculate_accuracy(test_loader)
        # Expect 50% (2 of 4 correct)
        assert np.isclose(accuracy, 50.0)


def test_evaluate_validation(trainer_mock):
    """Test Validation Metrics (Loss and Accuracy)."""
    trainer = trainer_mock

    mock_loss = 0.5
    mock_outputs = []

    for _, y_batch in trainer.val_loader:
        batch_size = y_batch.size(0)
        output = torch.zeros(batch_size, MOCK_OUTPUT_SIZE)

        for i, label in enumerate(y_batch):
            output[i, label] = 10.0

        mock_outputs.append(output)

    with patch.object(
        trainer.criterion, "forward", return_value=torch.tensor(mock_loss)
    ):
        with patch.object(trainer.model, "forward", side_effect=mock_outputs):
            val_loss, val_acc = trainer.calculate_validation()

            assert np.isclose(val_loss, mock_loss)
            assert np.isclose(val_acc, 100.0)


@patch("os.makedirs")
@patch("backend.ai.training.trainer.plt.savefig")
@patch("backend.ai.training.trainer.plt.subplots")
@patch("backend.ai.training.trainer.plt.tight_layout")
def test_plot_metrics(
    mock_tight_layout, mock_subplots, mock_savefig, mock_makedirs, trainer_mock
):
    """Test if plot_metrics uses the correct Matplotlib-Functions."""
    trainer = trainer_mock

    # Fake-Metrics
    losses = [0.1, 0.05]
    avg_losses = [0.2, 0.1]
    train_accuracies = [80, 90]
    val_losses = [0.3, 0.2]
    val_accuracies = [70, 85]

    mock_ax1 = MagicMock()
    mock_ax2 = MagicMock()

    mock_subplots.return_value = (MagicMock(), [mock_ax1, mock_ax2])

    # makedirs was called before
    mock_makedirs.reset_mock()
    trainer.plot_metrics(
        losses, avg_losses, train_accuracies, val_losses, val_accuracies
    )

    mock_ax1.plot.assert_called_once()
    mock_ax2.plot.assert_called()
    # Validation Loss/Acc + Training Loss/Acc = 4
    mock_ax2.plot.call_count == 4
    mock_ax2.legend.assert_called_once()

    mock_savefig.assert_called_once()
    mock_makedirs.assert_called_once()


@patch("os.makedirs")
@patch("torch.save")
def test_save_model(mock_torch_save, mock_makedirs, trainer_mock):
    """Test if save_model creates a new pickle-File."""
    trainer = trainer_mock

    mock_makedirs.reset_mock()

    trainer.save_model()

    mock_makedirs.assert_called_once()

    mock_torch_save.assert_called_once()
    # first element call_args: state_dict
    assert mock_torch_save.call_args[0][0].keys() == trainer.model.state_dict().keys()

    # second element call_args: file_name
    filename_arg = mock_torch_save.call_args[0][1]
    assert isinstance(filename_arg, str)
    assert filename_arg.endswith(".pt")
    assert "model_ffn_" in filename_arg


def test_trainer_train(trainer_mock):
    """Tests the whole train()-Workflow."""
    NUM_EPOCHS_TEST = 3
    MOCK_BATCH_LOSS = torch.tensor(0.5, requires_grad=True)
    MOCK_VAL_LOSS = 0.4

    trainer = trainer_mock
    # Enable Scheduler
    trainer.scheduler = MagicMock()

    NUM_BATCHES = len(trainer.train_loader)

    # Mock all Methods inside train()
    trainer.model.forward = MagicMock(return_value=torch.zeros(2, MOCK_OUTPUT_SIZE))
    trainer.criterion = MagicMock(return_value=MOCK_BATCH_LOSS)
    trainer.calculate_accuracy = MagicMock(side_effect=[80.0, 85.0, 90.0])
    trainer.calculate_validation = MagicMock(
        side_effect=[
            (MOCK_VAL_LOSS, 70.0),
            (MOCK_VAL_LOSS - 0.1, 75.0),
            (MOCK_VAL_LOSS - 0.2, 80.0),
        ]
    )
    trainer.plot_metrics = MagicMock()
    trainer.save_model = MagicMock()

    trainer.train(epochs=NUM_EPOCHS_TEST)

    # Loss Calculation per Epoch equals Batch Size
    expected_criterion_calls = NUM_EPOCHS_TEST * NUM_BATCHES
    trainer.criterion.assert_called()
    assert trainer.criterion.call_count == expected_criterion_calls

    # Acc. and Val. is calculated for each Epoch
    trainer.calculate_accuracy.assert_called()
    assert trainer.calculate_accuracy.call_count == NUM_EPOCHS_TEST

    trainer.calculate_validation.assert_called()
    assert trainer.calculate_validation.call_count == NUM_EPOCHS_TEST

    trainer.plot_metrics.assert_called_once()
    trainer.save_model.assert_called_once()

    # Scheduler called each Epoch
    trainer.scheduler.step.assert_called()
    assert trainer.scheduler.step.call_count == NUM_EPOCHS_TEST

    # Test epochs=None
    with patch("backend.ai.training.trainer.TrainingConfig") as MockConfig:
        MockConfig.NUM_EPOCHS = 5
        trainer_default = trainer_mock

        trainer_default.criterion = MagicMock(return_value=MOCK_BATCH_LOSS)
        trainer_default.calculate_accuracy = MagicMock(return_value=80.0)
        trainer_default.calculate_validation = MagicMock(
            return_value=(MOCK_VAL_LOSS, 70.0)
        )
        trainer_default.plot_metrics = MagicMock()
        trainer_default.save_model = MagicMock()

        trainer_default.train(epochs=None)  # -> Uses Default from params.py

        expected_calls_default = 5
        assert trainer_default.calculate_accuracy.call_count == expected_calls_default


def test_trainer_early_stopping(trainer_mock):
    """Tests if training stops when validation loss does not improve."""
    trainer = trainer_mock

    with patch("backend.ai.training.trainer.TrainingConfig") as MockConfig:
        MockConfig.EARLY_STOPPING_ACTIVE = True
        MockConfig.EARLY_STOPPING_PATIENCE = 2
        MockConfig.NUM_EPOCHS = 10

        trainer.model.forward = MagicMock(return_value=torch.zeros(2, MOCK_OUTPUT_SIZE))
        trainer.criterion = MagicMock(
            return_value=torch.tensor(0.5, requires_grad=True)
        )
        trainer.calculate_accuracy = MagicMock(return_value=100.0)
        trainer.plot_metrics = MagicMock()
        trainer.save_model = MagicMock()

        trainer.calculate_validation = MagicMock(
            side_effect=[(1.0, 80.0), (1.1, 80.0), (1.2, 80.0)]
        )
        trainer.train(epochs=None)

        assert trainer.calculate_validation.call_count == 3


@patch("os.makedirs")
@patch("backend.ai.training.trainer.plt.savefig")
@patch("backend.ai.training.trainer.plt.subplots")
def test_plot_metrics_with_smoothing(
    mock_subplots, mock_savefig, mock_makedirs, trainer_mock
):
    """Tests if moving average trend is plotted."""
    trainer = trainer_mock

    # Create more than 100 Losses
    losses = [0.5] * 150
    avg_losses = [0.5] * 2
    train_acc = [90] * 2
    val_losses = [0.5] * 2
    val_acc = [85] * 2

    mock_ax1 = MagicMock()
    mock_ax2 = MagicMock()
    mock_ax_acc = MagicMock()
    mock_ax2.twinx.return_value = mock_ax_acc

    mock_subplots.return_value = (MagicMock(), [mock_ax1, mock_ax2])

    trainer.plot_metrics(losses, avg_losses, train_acc, val_losses, val_acc)

    assert mock_ax1.plot.call_count == 2
    args, kwargs = mock_ax1.plot.call_args
    assert kwargs["label"] == "Trend (Moving Avg)"


def test_trainer_no_early_stopping_updates_best_model(trainer_mock):
    """Tests if best model state is saved when early stopping is disabled."""
    trainer = trainer_mock

    with patch("backend.ai.training.trainer.TrainingConfig") as MockConfig:
        MockConfig.EARLY_STOPPING_ACTIVE = False

        trainer.model.forward = MagicMock(return_value=torch.zeros(2, MOCK_OUTPUT_SIZE))
        trainer.criterion = MagicMock(
            return_value=torch.tensor(0.5, requires_grad=True)
        )
        trainer.calculate_validation = MagicMock(side_effect=[(0.5, 80.0), (0.3, 85.0)])
        trainer.plot_metrics = MagicMock()
        trainer.save_model = MagicMock()

        dummy_state_dict = {"weights": torch.tensor([1.0])}
        trainer.model.state_dict = MagicMock(return_value=dummy_state_dict)
        trainer.model.load_state_dict = MagicMock()

        trainer.train(epochs=2)

        trainer.model.load_state_dict.assert_called_with(dummy_state_dict)
