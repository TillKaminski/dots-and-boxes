"""Test Class for Game Setup and Logic."""

import sys
import os
import numpy as np
from game.game_board import GameBoard, Orientation
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def create_test_board():
    """Returns a 4x4 Board for Testing Purposes.

    Player 1 begins. Positions needed to complete boxes: vertical (1, 0)
    and horizontal (1, 3).
    """
    board = GameBoard(4)

    # Player 1 edges
    board.edges_horizontal[0, 0] = 1
    board.edges_horizontal[0, 1] = 1
    board.edges_vertical[0, 0] = 1

    # Player 2 edges
    board.edges_horizontal[1, 2] = 2
    board.edges_vertical[1, 2] = 2
    board.edges_vertical[2, 2] = 2

    board.current_player = 1

    return board


def test_board_initialization():
    """Test for Board Constructor."""
    size = 3
    board = GameBoard(size=size)

    # Check Board Shape
    assert board.edges_horizontal.shape == (size, size + 1)
    assert board.edges_vertical.shape == (size + 1, size)
    assert board.boxes.shape == (size, size)

    # Check Board Configuration
    assert np.all(board.edges_horizontal == 0)
    assert np.all(board.edges_vertical == 0)
    assert np.all(board.boxes == 0)

    # Check Scores
    assert board.scores == {1: 0, 2: 0}
    assert board.current_player == 0


def test_move(capsys):
    """Test for valid Turns (PLACEHOLDER)."""
    size = 3
    board = GameBoard(size=size)
    board.move(2, 4, Orientation.VERTICAL)
    captured = capsys.readouterr()
    assert (
        captured.out == "Board.move() called: row = 2, col = 4 - Orientation.VERTICAL\n"
    )
    assert captured.err == ""


def test_move_validity(create_test_board):
    """Test if an already occupied edge throws an Error."""
    board: GameBoard = create_test_board
    current_player = board.current_player
    # Already taken by Player 1
    row_occ, col_occ, orientation_occ = 0, 0, Orientation.HORIZONTAL
    with pytest.raises(ValueError):
        board.move(row_occ, col_occ, orientation_occ)

    row_free, col_free, orientation_free = 3, 3, Orientation.HORIZONTAL
    board.move(row_free, col_free, orientation_free)

    # Edge belongs to Player
    assert board.edges_horizontal[row_free, col_free] == current_player
    # Player Switch
    assert board.current_player != current_player


def test_move_out_of_bounds(create_test_board):
    """Test if invalid Positions are rejected."""
    board: GameBoard = create_test_board
    row_invalid, col_invalid, orientation = 10, 10, Orientation.VERTICAL

    with pytest.raises(ValueError):
        board.move(row_invalid, col_invalid, orientation)


def test_move_close_box(create_test_board):
    """Test Score Updates and Turn passes if no box completed."""
    board: GameBoard = create_test_board
    player_before = board.current_player
    score_before = board.scores[player_before]
    # Last edge for box (1, 2)
    row, col, orientation = 1, 3, Orientation.HORIZONTAL
    board.move(row, col, orientation)
    assert board.current_player == player_before
    assert board.scores[player_before] == score_before + 1
    assert board.boxes[1, 2] == player_before


def test_move_multiple_boxes(create_test_board):
    """Test if scoring multiple boxes in a row is possible."""
    board: GameBoard = create_test_board
    # Remember initial Values
    player_before = board.current_player
    score_before = board.scores[player_before]

    # First Box (0, 0)
    row_first, col_first, orientation_first = 1, 0, Orientation.VERTICAL
    board.move(row_first, col_first, orientation_first)
    assert board.current_player == player_before
    assert board.scores[player_before] == score_before + 1
    assert board.boxes[0, 0] == player_before

    # Second Box (1, 2)
    row_second, col_second, orientation_second = 1, 3, Orientation.HORIZONTAL
    board.move(row_second, col_second, orientation_second)
    assert board.current_player == player_before
    assert board.scores[player_before] == score_before + 2
    assert board.boxes[1, 2] == player_before
