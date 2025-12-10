"""Test Class for Random Bot."""

import pytest
import numpy as np
from unittest.mock import patch

from ai.bots.rule_based_bot import RuleBasedBot
from ai.bots.move import Move
from game.game_board import Orientation


GAME_SIZE = 3


# Create Fixtures for the different Game States
@pytest.fixture
def rule_based_bot() -> RuleBasedBot:
    """Fixture for a RuleBasedBot instance (size: 3x3)."""
    return RuleBasedBot(GAME_SIZE)


@pytest.fixture
def setup_win_state(rule_based_bot):
    """Sets up a state where a winning move (-1 box) is available."""
    rule_based_bot.update(x=0, y=1, orientation=Orientation.HORIZONTAL)
    rule_based_bot.update(x=0, y=0, orientation=Orientation.VERTICAL)
    rule_based_bot.update(x=1, y=0, orientation=Orientation.VERTICAL)
    win_move = Move(0, 0, Orientation.HORIZONTAL)
    return rule_based_bot, win_move


@pytest.fixture
def setup_prod_win_state(rule_based_bot):
    """Sets up a state where 'generating a win' is the next best move (-3 box).

    returns: Set up Bot, list of prioritized Moves
    """
    rule_based_bot.update(x=1, y=1, orientation=Orientation.VERTICAL)
    generate_win_moves = [
        Move(1, 2, Orientation.HORIZONTAL),
        Move(1, 1, Orientation.HORIZONTAL),
        Move(0, 2, Orientation.HORIZONTAL),
        Move(0, 1, Orientation.HORIZONTAL),
    ]

    return rule_based_bot, generate_win_moves


@pytest.fixture
def setup_neutral_state(rule_based_bot):
    """Sets up a state where a 'neutral' move is available (targeting a -4 box)."""
    rule_based_bot.boxes[:] = -2
    rule_based_bot.boxes[0, 0] = -4

    neutral_move = Move(0, 0, Orientation.VERTICAL)
    return rule_based_bot, neutral_move


@pytest.fixture
def setup_fallback_state(rule_based_bot):
    """Sets the bot state so that only the 'fallback' (random choice) is used."""
    rule_based_bot.boxes[:] = -2
    fallback_move = rule_based_bot.positions[0]
    return rule_based_bot, fallback_move


def test_bot_constructor(rule_based_bot):
    """Test Bot-Constructor."""
    expected_positions = 2 * GAME_SIZE * (GAME_SIZE + 1)
    assert len(rule_based_bot.positions) == expected_positions

    for pos in rule_based_bot.positions:
        assert pos.available

    assert rule_based_bot.boxes.shape == (GAME_SIZE, GAME_SIZE)
    assert np.all(rule_based_bot.boxes == -4)

    assert rule_based_bot.name() == "rule_based"


def test_move_returns_valid_move_dict(rule_based_bot):
    """Random-Bot should return a valid move dict."""
    move = rule_based_bot.move(return_dictionary=True)
    assert "x" in move and "y" in move and "orientation" in move
    assert isinstance(move["x"], int)
    assert isinstance(move["y"], int)
    assert move["orientation"] in ["horizontal", "vertical"]


def test_move_logging(rule_based_bot):
    """Test Terminal Logging has no impact on Bot Behavior."""
    move = rule_based_bot.move(log_move=True)
    assert isinstance(move, Move)

    for pos in rule_based_bot.positions:
        pos.update()

    with pytest.raises(RuntimeError, match="No possible Moves available."):
        rule_based_bot.move(log_move=True)


def test_bot_reset(rule_based_bot):
    """Test that reset makes all moves available again."""
    first_move = rule_based_bot.positions[0]
    rule_based_bot.update(first_move.x, first_move.y, first_move.orientation)

    assert not first_move.available
    rule_based_bot.reset()

    expected_positions = 2 * GAME_SIZE * (GAME_SIZE + 1)
    assert len(rule_based_bot.positions) == expected_positions

    # Check all moves are available again
    assert all(move.available for move in rule_based_bot.positions)


def test_move_no_possible_moves_raises_error(rule_based_bot):
    """Test that move() raises RuntimeError when no moves are available."""
    for m in rule_based_bot.positions:
        m.update()
    with pytest.raises(RuntimeError, match="No possible Moves available."):
        rule_based_bot.move(log_move=True)


def test_update_marks_move_unavailable(rule_based_bot):
    """After update, the specific move should be unavailable."""
    first_move = rule_based_bot.positions[0]
    rule_based_bot.update(first_move.x, first_move.y, first_move.orientation)

    assert not rule_based_bot.positions[0].available


def test_box_tracking(rule_based_bot):
    """Test box tracking and completion (-1 -> 1)."""
    # Fill the Board stepwise
    rule_based_bot.update(x=0, y=0, orientation=Orientation.HORIZONTAL)
    assert rule_based_bot.boxes[0][0] == -3

    rule_based_bot.update(x=0, y=0, orientation=Orientation.VERTICAL)
    assert rule_based_bot.boxes[0][0] == -2

    rule_based_bot.update(x=0, y=1, orientation=Orientation.HORIZONTAL)
    assert rule_based_bot.boxes[0][0] == -1

    rule_based_bot.update(x=1, y=0, orientation=Orientation.VERTICAL)
    assert rule_based_bot.boxes[0][0] == 1

    # Create Win Position for Box [1, 1]
    rule_based_bot.boxes[1, 1] = -1
    rule_based_bot.update(1, 2, Orientation.HORIZONTAL)
    assert rule_based_bot.boxes[1, 1] == 1


def test_update_horizontal_edge(rule_based_bot):
    """Test update for horizontal moves at board edges (top and bottom)."""
    # Edge Horizontal (0, 0) affects only box above (0, 0)
    rule_based_bot.update(0, 0, Orientation.HORIZONTAL)
    assert rule_based_bot.boxes[0, 0] == -3

    # Edge Horizontal (0, max) affects only box below (0, GAME_SIZE-1)
    rule_based_bot.update(0, rule_based_bot.size, Orientation.HORIZONTAL)
    assert rule_based_bot.boxes[0, rule_based_bot.size - 1] == -3


def test_update_vertical_edge(rule_based_bot):
    """Test update for vertical moves at board edges (left and right)."""
    # Left Edge: (0, 0) Vertical affects only box right (0, 0)
    rule_based_bot.update(0, 0, Orientation.VERTICAL)
    assert rule_based_bot.boxes[0, 0] == -3

    # Right Edge: (GAME_SIZE, 0) Vertical affects only box left (GAME_SIZE-1, 0)
    rule_based_bot.update(rule_based_bot.size, 0, Orientation.VERTICAL)
    assert rule_based_bot.boxes[rule_based_bot.size - 1, 0] == -3


def test_helper_get_adjacent_boxes(rule_based_bot):
    """Test _get_adjacent_boxes for horizontal and vertical moves (mid and edges)."""
    # Horizontal Mid
    move_h_mid = Move(1, 1, Orientation.HORIZONTAL)
    assert rule_based_bot._get_adjacent_boxes(move_h_mid) == [(1, 1), (1, 0)]

    # Vertical Mid
    move_v_mid = Move(1, 1, Orientation.VERTICAL)
    assert rule_based_bot._get_adjacent_boxes(move_v_mid) == [(1, 1), (0, 1)]

    # Horizontal Bottom Edge (0, 0)
    move_h_top = Move(0, 0, Orientation.HORIZONTAL)
    assert rule_based_bot._get_adjacent_boxes(move_h_top) == [(0, 0)]

    # Vertical Left Edge (0, 0)
    move_v_left = Move(0, 0, Orientation.VERTICAL)
    assert rule_based_bot._get_adjacent_boxes(move_v_left) == [(0, 0)]


def test_move_return_values(rule_based_bot):
    """Test move() returns valid Move object and dictionary structure."""
    # Return Move-Object
    move = rule_based_bot.move(return_dictionary=False)
    assert isinstance(move, Move)
    assert move.orientation in [Orientation.HORIZONTAL, Orientation.VERTICAL]

    # Return Dictionary
    move_dict = rule_based_bot.move(return_dictionary=True)
    assert isinstance(move_dict, dict)
    assert "x" in move_dict and "y" in move_dict and "orientation" in move_dict
    assert isinstance(move_dict["x"], int)
    assert move_dict["orientation"] in ["horizontal", "vertical"]


def test_move_priority_win(setup_win_state):
    """Test move highest priority: win (-1 box)."""
    bot, expected_move = setup_win_state

    # Override positions (contains one element)
    bot.positions.clear()
    bot.positions = [expected_move]

    move = bot.move()
    assert move == expected_move

    # Test dictionary return
    dict = bot.move(return_dictionary=True)
    assert dict["x"] == expected_move.x
    assert dict["y"] == expected_move.y
    assert dict["orientation"] == expected_move.orientation.name.lower()


def test_move_priority_produce_win(setup_prod_win_state):
    """Tests the second priority: creating a two-edge box (-3 box)."""
    bot, expected_moves = setup_prod_win_state

    move = bot.move()
    assert move in expected_moves


def test_move_priority_neutral(setup_neutral_state):
    """Tests the third priority: making a neutral move (targeting a -4 box)."""
    bot, expected_move = setup_neutral_state

    bot.positions.clear()
    bot.positions = [expected_move]

    actual_move = bot.move()
    assert actual_move == expected_move


def test_move_priority_fallback(setup_fallback_state):
    """Tests the lowest priority: random choice when no priority moves exist."""
    bot, _ = setup_fallback_state

    available_moves = bot.positions[:5]
    bot.positions = available_moves
    expected_move = available_moves[0]

    # Mock Random Choice
    with patch("random.choice") as mock_choice:
        mock_choice.return_value = expected_move

        actual_move = bot.move()
        assert actual_move == expected_move

        actual_dict = bot.move(return_dictionary=True)
        assert actual_dict["x"] == expected_move.x
        assert actual_dict["y"] == expected_move.x
        assert actual_dict["orientation"] == expected_move.orientation.name.lower()
