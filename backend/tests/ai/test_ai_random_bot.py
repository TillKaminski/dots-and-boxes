"""Test Class for Random Bot."""

import pytest
from ai.bots.random_bot import RandomBot
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
    move = bot.move(ret_dict=True)
    assert "x" in move and "y" in move and "orientation" in move
    assert isinstance(move["x"], int)
    assert isinstance(move["y"], int)
    assert move["orientation"] in ["horizontal", "vertical"]


def test_move_returns_valid_move(bot):
    """Random-Bot should return a valid move dict."""
    move = bot.move()
    assert isinstance(move.x, int)
    assert isinstance(move.x, int)
    assert move.orientation in [Orientation.HORIZONTAL, Orientation.VERTICAL]


def test_update_positions(bot):
    """After update, move should be unavailable."""
    move = bot.move(ret_dict=False)
    bot.update_positions(move.x, move.y, move.orientation)
    match = [
        m
        for m in bot.positions
        if m.x == move.x and m.y == move.y and m.orientation == move.orientation
    ][0]
    assert not match.available


def test_move_logging(bot, capsys):
    """Test Terminal Messages."""
    for pos in bot.positions:
        pos.update()

    with pytest.raises(RuntimeError, match="No possible Moves available."):
        bot.move(log_move=True)
    output = capsys.readouterr()
    assert "No possible Moves available." in output.out

    bot.reset()

    bot.move(log_move=True)
    output = capsys.readouterr()
    assert "RandomBot move" in output.out

    bot.move(ret_dict=True, log_move=True)
    output = capsys.readouterr()
    assert "RandomBot move" in output.out


def test_bot_restart(bot):
    """Test Bot Restart."""
    for pos in bot.positions:
        pos.update()

    for pos in bot.positions:
        assert not pos.available

    bot.reset()
    for pos in bot.positions:
        assert pos.available


def test_move_exhaustion(bot):
    """When all moves are used, should raise error."""
    for m in bot.positions:
        m.update()
    with pytest.raises(RuntimeError):
        bot.move()
