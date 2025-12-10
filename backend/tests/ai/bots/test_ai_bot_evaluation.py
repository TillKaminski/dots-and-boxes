"""Tests for Bot-Evaluator Class."""

import pytest

from ai.bots.random_bot import RandomBot
from game.game_service import GameService
from ai.bots.evaluation import BotEvaluator


BOARD_SIZE = 1
N_GAMES = 4

bot1 = RandomBot(size=BOARD_SIZE)
bot2 = RandomBot(size=BOARD_SIZE)


@pytest.fixture
def create_test_evaluator() -> BotEvaluator:
    """Setup for each Unit Test."""
    service = GameService()
    evaluator: BotEvaluator = BotEvaluator(service, board_size=BOARD_SIZE)
    return evaluator


def test_evaluate_alternate_mode(create_test_evaluator):
    """Test if Alternate Mode leads to an equal Win-rate (Second Player always wins)."""
    n_games = N_GAMES

    results = create_test_evaluator.evaluate(
        bot1, bot2, n_games=n_games, start_mode="alternate"
    )

    assert results["games"] == 4
    assert results["wins_bot1"] == 2
    assert results["wins_bot2"] == 2
    assert results["draws"] == 0
    assert results["win_rate_bot1"] == 0.5

    assert results["avg_score_bot1"] > 0
    assert results["avg_score_bot1"] == results["avg_score_bot2"]


def test_evaluate_fixed_mode(create_test_evaluator):
    """Test fixed mode: Bot1 starts, Bot2 always wins."""
    n_games = N_GAMES

    results = create_test_evaluator.evaluate(
        bot1, bot2, n_games=n_games, start_mode="fixed"
    )

    assert results["games"] == 4
    assert results["wins_bot1"] == 0
    assert results["wins_bot2"] == 4

    assert results["win_rate_bot1"] == 0.0
    assert results["win_rate_bot2"] == 1.0

    # Bot2 always gets 1 Box
    assert results["avg_score_bot1"] == 0.0
    assert results["avg_score_bot2"] == 1.0


def test_evaluate_random_mode_controlled(create_test_evaluator):
    """Test random mode: Metrics should be in a plausible range."""
    n_games = 100

    results = create_test_evaluator.evaluate(
        bot1, bot2, n_games=n_games, start_mode="random"
    )

    # Check if Metrics are in a plausible range
    assert results["games"] == n_games
    assert results["wins_bot1"] <= n_games
    assert results["wins_bot2"] <= n_games
    assert results["draws"] <= n_games

    assert results["win_rate_bot1"] <= 1.0
    assert results["win_rate_bot1"] >= 0.0


def test_evaluate_save_moves_false(create_test_evaluator):
    """Test if save_moves has an impact on Metrics."""
    n_games = 1

    results = create_test_evaluator.evaluate(
        bot1, bot2, n_games=n_games, start_mode="fixed", save_moves=False
    )

    assert results["games"] == 1
    assert results["wins_bot1"] == 0
    assert results["wins_bot2"] == 1
