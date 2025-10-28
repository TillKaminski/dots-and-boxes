"""Test Class for Game Setup and Logic."""

import sys
import os
import numpy as np
from game.game_board import GameBoard
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def create_test_board():
    """Returns a 4x4 Board for Testing Purposes.

    Player 1 begins. Positions (0, 1) and (1, 3) are missing edges for a box closure.
    """
    board = GameBoard(4)

    # Player 1 edges
    board.edges_horizontal[0, 0] = 1
    board.edges_horizontal[1, 0] = 1
    board.edges_vertical[0, 0] = 1

    # Player 2 edges
    board.edges_horizontal[1, 2] = 2
    board.edges_horizontal[2, 2] = 2
    board.edges_vertical[1, 2] = 2

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
    """Test for valid Turns."""
    size = 3
    board = GameBoard(size=size)
    row, col = board.move(2, 4)
    captured = capsys.readouterr()
    assert captured.out == "Board.move() called with row = 2, col = 4\n"
    assert captured.err == ""
    assert row == 2
    assert col == 4
