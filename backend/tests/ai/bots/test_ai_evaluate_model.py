"""Tests for the Model Evaluation script."""

import argparse
from unittest.mock import patch, MagicMock
from ai.bots import evaluate_model

MOCK_RESULTS = {
    "bot1_name": "Bot1",
    "bot2_name": "Bot2",
    "wins_bot1": 5,
    "win_rate_bot1": 0.5,
    "wins_bot2": 5,
    "win_rate_bot2": 0.5,
    "draws": 0,
    "avg_score_bot1": 1.0,
    "avg_score_bot2": 1.0,
}


@patch("ai.bots.bot_service.BotService.create_bot")
@patch("ai.bots.evaluator.BotEvaluator.evaluate", return_value=MOCK_RESULTS)
@patch("argparse.ArgumentParser.parse_args")
def test_main_evaluation_flow(mock_args, mock_eval, mock_create, capsys):
    """Test if the evaluator is called with the correct parameters."""
    mock_args.return_value = argparse.Namespace(
        n=50,
        size=3,
        bot1="ffn",
        bot2="rule",
        model=None,
        epsilon=None,
        model2=None,
        epsilon2=None,
    )

    m1, m2 = MagicMock(), MagicMock()
    m1.BOT_NAME = "Bot1"
    m2.BOT_NAME = "Bot2"
    mock_create.side_effect = [m1, m2]

    evaluate_model.main()
    captured = capsys.readouterr()

    assert mock_create.call_count == 2
    mock_eval.assert_called_once()
    assert mock_eval.call_args[1]["n_games"] == 50
    assert "### Evaluating Bot1 vs Bot2 (50 Games) ###" in captured.out
    assert "RESULTS for Bot1 vs Bot2" in captured.out


@patch("ai.bots.bot_service.BotService.create_bot")
@patch("ai.bots.evaluator.BotEvaluator.evaluate", return_value=MOCK_RESULTS)
@patch("argparse.ArgumentParser.parse_args")
def test_main_with_epsilon_parameters(mock_args, mock_eval, mock_create, capsys):
    """Test if epsilon values are correctly printed in the output."""
    mock_args.return_value = argparse.Namespace(
        n=10,
        size=2,
        bot1="ffn",
        bot2="ffn",
        model=None,
        epsilon=0.1,
        model2=None,
        epsilon2=0.2,
    )

    m1, m2 = MagicMock(), MagicMock()
    m1.BOT_NAME = "Bot1"
    m2.BOT_NAME = "Bot2"
    mock_create.side_effect = [m1, m2]

    evaluate_model.main()
    captured = capsys.readouterr()

    assert "epsilon=0.1" in captured.out
    assert "epsilon=0.2" in captured.out
