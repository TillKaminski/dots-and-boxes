"""Test Training Class."""

from unittest.mock import patch, MagicMock
from ai.training import training


@patch("ai.training.training.ModelTrainer")
def test_training_default(trainer, capsys):
    """Test Terminal Output."""
    mock = trainer.return_value
    mock.train = MagicMock()

    training.main()

    captured = capsys.readouterr()

    assert len(captured.out) > 0
    assert "error" not in captured.out

    mock.train.assert_called_once()


@patch("ai.training.training.ModelTrainer")
def test_training_input(trainer, capsys):
    """Test Terminal Output contains User Input."""
    mock = trainer.return_value
    mock.train = MagicMock()

    training.main(it=250)

    captured = capsys.readouterr()

    assert "250" in captured.out
    mock.train.assert_called_once()
