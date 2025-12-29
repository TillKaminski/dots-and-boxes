"""Test Training Class."""

import argparse
from unittest.mock import patch, MagicMock
from ai.training import training


def _mock_main_execution(iterations):
    """Helper Function that simulates Terminal Execution."""
    mock_args = argparse.Namespace(it=iterations, src="")

    with patch(
        "ai.training.training.argparse.ArgumentParser.parse_args",
        return_value=mock_args,
    ):
        with patch("ai.training.training.ModelTrainer") as MockTrainer:
            MockTrainer.return_value.train = MagicMock()
            training.main()
            return MockTrainer.return_value.train


def test_main_with_iteration_parameter(capsys):
    """Test, if train() Method is called with parameters."""
    expected_iterations = 50
    mock_train = _mock_main_execution(iterations=expected_iterations)

    captured = capsys.readouterr()

    mock_train.assert_called_once_with(expected_iterations)

    assert f"Start Training ({expected_iterations} Iterations)" in captured.out
    assert "Training finished." in captured.out


def test_main_default_iterations(capsys):
    """Test, if train() Method is called with default value."""
    mock_train = _mock_main_execution(iterations=0)

    captured = capsys.readouterr()

    mock_train.assert_called_once_with(None)

    assert "Start Training (default Iterations)" in captured.out
    assert "Training finished." in captured.out
