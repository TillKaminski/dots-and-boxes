"""Test Class for Random Bot."""

import pytest
from ai.bots.random_bot import RandomBot
from ai.bots.move import Move
from game.game_board import Orientation

bot_size = 4


@pytest.fixture
def bot():
    """Create a Bot Instance for each Test."""
    return RandomBot(bot_size)


def test_random_bot_constructor(bot):
    """Test all positions are initialized correctly."""
    assert len(bot.positions) == bot.size * (bot.size + 1) * 2

    for pos in bot.positions:
        assert pos.available


def test_move_returns_valid_move_dict(bot):
    """Random-Bot should return a valid move dict."""
    move = bot.move(return_dictionary=True)
    assert "x" in move and "y" in move and "orientation" in move
    assert isinstance(move["x"], int)
    assert isinstance(move["y"], int)
    assert move["orientation"] in ["horizontal", "vertical"]


def test_move_returns_valid_move(bot):
    """Random-Bot should return a valid move dict."""
    move: Move = bot.move()
    assert isinstance(move.x, int)
    assert isinstance(move.x, int)
    assert move.orientation in [Orientation.HORIZONTAL, Orientation.VERTICAL]


def test_update_positions(bot):
    """After update, move should be unavailable."""
    move = bot.move(return_dictionary=False)
    bot.update(move.x, move.y, move.orientation)
    match = [
        m
        for m in bot.positions
        if m.x == move.x and m.y == move.y and m.orientation == move.orientation
    ][0]
    assert not match.available


def test_move_logging(bot, capsys):
    """Test Terminal Logging has no impact on Bot Behavior."""
    move = bot.move(log_move=True)
    assert isinstance(move, Move)

    for pos in bot.positions:
        pos.update()

    with pytest.raises(RuntimeError, match="No possible Moves available."):
        bot.move(log_move=True)


def test_bot_restart(bot):
    """Bot Restart resets all positions."""
    for pos in bot.positions:
        pos.update()

    for pos in bot.positions:
        assert not pos.available

    bot.reset()
    for pos in bot.positions:
        assert pos.available


def test_move_not_possible(bot):
    """Move with no positions available should raise error."""
    for m in bot.positions:
        m.update()
    with pytest.raises(RuntimeError):
        bot.move()


def test_name(bot):
    """Name-Method should return Model Name."""
    assert bot.name() == RandomBot.BOT_NAME
