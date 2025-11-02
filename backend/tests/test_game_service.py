"""Test Class for Service-Tests."""

import pytest
from game.game_board import Orientation
from game.game_service import GameService

from game.errors import (
    ERROR_EDGE_TAKEN,
    ERROR_GAME_OVER,
    ERROR_OUT_OF_BOUNDS,
    ERROR_INVALID_ORIENTATION,
)


@pytest.fixture
def service():
    """Creates a new Game-Service Object with 2x2 Board."""
    return GameService(size=2)


def test_initial_state(service):
    """Test new Game initialization."""
    state = service.get_state()

    # Check Structure
    assert isinstance(state, dict)
    assert state["size"] == 2
    assert "edges" in state
    assert "boxes" in state
    assert state["scores"] == {1: 0, 2: 0}
    assert state["finished"] is False
    assert state["currentPlayer"] == 1

    # All Edges free
    assert all(val == 0 for row in state["edges"]["horizontal"] for val in row)
    assert all(val == 0 for row in state["edges"]["vertical"] for val in row)

    # All Boxes empty
    assert all(val == -4 for row in state["boxes"] for val in row)


def test_make_move_changes_state(service):
    """Test if Player Action changes Board Configuration."""
    # Create a closed box and check Board
    actions = [
        (0, 0, Orientation.HORIZONTAL),  # P1
        (0, 1, Orientation.HORIZONTAL),  # P2
        (0, 0, Orientation.VERTICAL),  # P1
        (1, 0, Orientation.VERTICAL),  # P2 scores (0, 0)
    ]

    for action in actions:
        service.make_move(*action)

    result = service.get_state()

    assert result["currentPlayer"] == 2
    assert result["edges"]["horizontal"][0][0] == 1
    assert result["edges"]["horizontal"][0][1] == 2
    assert result["edges"]["vertical"][0][0] == 1
    assert result["edges"]["vertical"][1][0] == 2
    assert result["boxes"][0][0] == 2
    assert result["finished"] is False
    assert result["scores"] == {1: 0, 2: 1}


def test_restart_game_resets_everything(service):
    """Test if Restart Calls empties everything."""
    service.make_move(0, 0, Orientation.HORIZONTAL)
    state_before = service.get_state()

    new_state = service.restart_game()

    assert new_state["currentPlayer"] == 1
    assert new_state["scores"] == {1: 0, 2: 0}
    # Check Board is empty
    assert all(val == 0 for row in new_state["edges"]["horizontal"] for val in row)
    assert all(val == 0 for row in new_state["edges"]["vertical"] for val in row)
    assert state_before != new_state


def test_game_over_detection(service):
    """Test if an Action triggers Game-Over Flag."""
    # Moves in 2x2 for Draw, all Edges filled
    moves = [
        (0, 0, Orientation.HORIZONTAL),  # Player 1
        (0, 0, Orientation.VERTICAL),  # Player 2
        (1, 0, Orientation.HORIZONTAL),  # Player 1
        (0, 1, Orientation.VERTICAL),  # Player 2
        (0, 1, Orientation.HORIZONTAL),  # Player 1
        (1, 0, Orientation.VERTICAL),  # Player 2 (score)
        (1, 1, Orientation.HORIZONTAL),  # Player 2
        (1, 1, Orientation.VERTICAL),  # Player 1
        (0, 2, Orientation.HORIZONTAL),  # Player 2 (score)
        (2, 1, Orientation.VERTICAL),  # Player 2
        (2, 2, Orientation.HORIZONTAL),  # Player 1 (score)
        (2, 2, Orientation.VERTICAL),  # Player 1 (score)
    ]

    for x, y, o in moves:
        service.make_move(x, y, o)

    assert isinstance(service.is_game_over(), bool)
    assert service.is_game_over()
    assert service.get_state()["finished"] is True
    assert service.get_winner() == "Draw"

    # Check Additional Moves after Game End
    prev_state = service.get_state().copy()
    assert service.make_move(0, 0, Orientation.HORIZONTAL) == ERROR_GAME_OVER
    assert service.get_state() == prev_state


def test_invalid_move(service):
    """Test if illegal moves (duplicate edges) returns an Error-Message."""
    service.make_move(0, 0, Orientation.HORIZONTAL)

    result = service.make_move(0, 0, Orientation.HORIZONTAL)
    assert result == ERROR_EDGE_TAKEN

    # Test-Board is smaller than 5x5
    result_out_of_bounds = service.make_move(5, 5, Orientation.HORIZONTAL)
    assert result_out_of_bounds == ERROR_OUT_OF_BOUNDS

    result_invalid_orientation = service.make_move(0, 0, None)
    assert result_invalid_orientation == ERROR_INVALID_ORIENTATION
