"""Test Class for Game Setup and Logic."""

import numpy as np
from game.game_board import GameBoard, Orientation, parse_orientation
import pytest

from game.errors import ERROR_EDGE_TAKEN, ERROR_OUT_OF_BOUNDS


@pytest.fixture
def create_test_board():
    """Returns a 4x4 Board for Testing Purposes.

    Player 1 begins. Positions needed to complete boxes: vertical (1, 0)
    and horizontal (1, 3).
    """
    board = GameBoard(4)
    board.current_player = 1

    board.move(0, 0, Orientation.HORIZONTAL)  # P1
    board.move(0, 1, Orientation.HORIZONTAL)  # P2
    board.move(0, 0, Orientation.VERTICAL)  # P1

    board.move(1, 2, Orientation.HORIZONTAL)  # P2
    board.move(1, 2, Orientation.VERTICAL)  # P1
    board.move(2, 2, Orientation.VERTICAL)  # P2

    return board


def test_board_initialization():
    """Test for Board Constructor."""
    size = 3
    board = GameBoard(size=size, starting_player=2)
    assert board.current_player == 2

    board = GameBoard(size=size)
    assert board.current_player == 1

    # Check Board Shape
    assert board.edges_horizontal.shape == (size, size + 1)
    assert board.edges_vertical.shape == (size + 1, size)
    assert board.boxes.shape == (size, size)

    # Check Board Configuration
    assert np.all(board.edges_horizontal == 0)
    assert np.all(board.edges_vertical == 0)
    assert np.all(board.boxes == -4)

    # Check Scores
    assert board.scores == {1: 0, 2: 0}


def test_move_rejects_occupied_edges(create_test_board):
    """Test if an already occupied edge throws an Error."""
    board: GameBoard = create_test_board
    current_player = board.current_player
    # Already taken by Player 1 (Horizontal)
    x_occ_h, y_occ_h, orientation_occ_h = 0, 0, Orientation.HORIZONTAL
    with pytest.raises(ValueError, match=ERROR_EDGE_TAKEN["error"]):
        board.move(x_occ_h, y_occ_h, orientation_occ_h)

    # Already taken by Player 2 (Vertical)
    x_occ_v, y_occ_v, orientation_occ_v = 1, 2, Orientation.VERTICAL
    with pytest.raises(ValueError, match=ERROR_EDGE_TAKEN["error"]):
        board.move(x_occ_v, y_occ_v, orientation_occ_v)

    x_free, y_free, orientation_free = 3, 3, Orientation.HORIZONTAL
    board.move(x_free, y_free, orientation_free)

    # Edge belongs to Player
    assert board.edges_horizontal[x_free, y_free] == current_player
    # Player Switch
    assert board.current_player != current_player


def test_move_out_of_bounds(create_test_board):
    """Test if invalid Positions are rejected."""
    board: GameBoard = create_test_board
    x_invalid, y_invalid, orientation = 10, 10, Orientation.VERTICAL

    with pytest.raises(ValueError, match=ERROR_OUT_OF_BOUNDS["error"]):
        board.move(x_invalid, y_invalid, orientation)

    # valid move
    board.move(3, 0, Orientation.HORIZONTAL)
    board.move(4, 0, Orientation.VERTICAL)

    # out of bounds
    with pytest.raises(ValueError, match=ERROR_OUT_OF_BOUNDS["error"]):
        board.move(4, 0, Orientation.HORIZONTAL)

    with pytest.raises(ValueError, match=ERROR_OUT_OF_BOUNDS["error"]):
        board.move(5, 0, Orientation.VERTICAL)

    with pytest.raises(ValueError, match=ERROR_OUT_OF_BOUNDS["error"]):
        board.move(-1, -1, Orientation.HORIZONTAL)


def test_move_box_updates(create_test_board):
    """Test all different box situations."""
    board: GameBoard = create_test_board

    # Boxes free: (2, 1) (2, 0) (3, 1)
    assert board.boxes[2, 1] == -4
    assert board.boxes[2, 0] == -4
    assert board.boxes[3, 1] == -4

    # Horizontal Edge between (2, 0) and (2, 1)
    x_1, y_1, o_1 = 2, 1, Orientation.HORIZONTAL
    board.move(x_1, y_1, o_1)
    assert board.boxes[2, 1] == -3
    assert board.boxes[2, 0] == -3

    # Vertical Edge between (2, 1) and (3, 1)
    x_2, y_2, o_2 = 3, 1, Orientation.VERTICAL
    board.move(x_2, y_2, o_2)
    assert board.boxes[2, 1] == -2
    assert board.boxes[3, 1] == -3


def test_move_scores_when_box_completed(create_test_board):
    """Test Score Updates and Turn passes if no box completed."""
    board: GameBoard = create_test_board
    player_before = board.current_player
    score_before = board.scores[player_before]
    # Last edge for box (1, 2)
    x, y, orientation = 1, 3, Orientation.HORIZONTAL
    board.move(x, y, orientation)
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
    x_first, y_first, orientation_first = 1, 0, Orientation.VERTICAL
    board.move(x_first, y_first, orientation_first)
    assert board.current_player == player_before
    assert board.scores[player_before] == score_before + 1
    assert board.boxes[0, 0] == player_before

    # Second Box (1, 2)
    x_second, y_second, orientation_second = 1, 3, Orientation.HORIZONTAL
    board.move(x_second, y_second, orientation_second)
    assert board.current_player == player_before
    assert board.scores[player_before] == score_before + 2
    assert board.boxes[1, 2] == player_before


def test_move_close_simultaneously(create_test_board):
    """Test if an Edge between two closed Boxes works."""
    board: GameBoard = create_test_board

    # Setup Box (1, 0)
    board.move(1, 0, Orientation.HORIZONTAL)
    board.move(1, 1, Orientation.HORIZONTAL)
    board.move(2, 0, Orientation.VERTICAL)

    current_player = board.current_player
    player_score = board.scores[current_player]
    # Close two Boxes: (1, 0) and (0, 0)
    board.move(1, 0, Orientation.VERTICAL)
    assert board.current_player == current_player
    assert board.scores[current_player] == player_score + 2
    # Two Boxes updated
    assert board.boxes[0, 0] == current_player
    assert board.boxes[1, 0] == current_player

    # Setup Box (1, 3)
    board.move(1, 4, Orientation.HORIZONTAL)
    board.move(1, 3, Orientation.VERTICAL)
    board.move(2, 3, Orientation.VERTICAL)

    current_player = board.current_player
    player_score = board.scores[current_player]
    # Close two Boxes: (1, 3) and (1, 2)
    board.move(1, 3, Orientation.HORIZONTAL)
    assert board.current_player == current_player
    assert board.scores[current_player] == player_score + 2
    # Two Boxes updated
    assert board.boxes[1, 3] == current_player
    assert board.boxes[1, 2] == current_player


def test_move_consistent_updates(create_test_board):
    """Test if Updates get overwritten."""
    board: GameBoard = create_test_board

    # Close first Box (0, 0)
    current_player = board.current_player
    board.move(1, 0, Orientation.VERTICAL)
    assert board.current_player == current_player
    assert board.boxes[0, 0] == current_player

    # Close second Box (1, 0)
    board.move(1, 0, Orientation.HORIZONTAL)
    board.move(1, 1, Orientation.HORIZONTAL)

    # Additional Move to switch players
    board.move(3, 1, Orientation.HORIZONTAL)
    assert board.current_player != current_player

    board.move(2, 0, Orientation.VERTICAL)
    assert board.boxes[1, 0] == board.current_player

    # Check Box (0, 0) for consistency
    assert board.boxes[0, 0] == current_player


def test_print_board_closed_box(capsys):
    """Tests print."""
    board = GameBoard(size=2)
    board.current_player = 1

    # Set Edged for Box (0, 0)
    board.move(0, 0, Orientation.HORIZONTAL)  # Player 1
    board.move(0, 0, Orientation.VERTICAL)  # Player 2
    board.move(0, 1, Orientation.HORIZONTAL)  # Player 1

    # Close Box
    board.move(1, 0, Orientation.VERTICAL)  # Player 2

    board.print_board()
    captured = capsys.readouterr()
    output = captured.out
    clean_output = [line.strip() for line in output.splitlines() if line.strip()]

    # Check Output line-wise
    assert "=====================" in clean_output[0]
    assert "#---1---#--- ---#" in clean_output[1]
    assert "|2 [2]  |2  3   |" in clean_output[2]
    assert "#---1---#--- ---#" in clean_output[3]
    assert "|   3   |   4   |" in clean_output[4]
    assert "#--- ---#--- ---#" in clean_output[5]
    assert "=====================" in clean_output[6]


def test_is_game_over():
    """Test if Win or Draw is detected."""
    # Board Configuration in which different Game Endings can be evaluated.
    board_configuration = [
        (0, 1, Orientation.VERTICAL),
        (1, 1, Orientation.VERTICAL),
        (2, 1, Orientation.VERTICAL),
        (0, 0, Orientation.VERTICAL),
        (1, 0, Orientation.VERTICAL),
        (2, 0, Orientation.VERTICAL),
        (0, 2, Orientation.HORIZONTAL),
        (1, 2, Orientation.HORIZONTAL),
    ]

    board_win_p1: GameBoard = GameBoard(size=2)
    board_win_p2: GameBoard = GameBoard(size=2)
    board_draw: GameBoard = GameBoard(size=2)

    # Setup Boards
    for config in board_configuration:
        board_win_p1.move(*config)
        board_win_p2.move(*config)
        board_draw.move(*config)

    # Current Player should be Player 1
    assert board_win_p1.current_player == 1
    assert board_win_p2.current_player == 1
    assert board_draw.current_player == 1

    # No Points earned
    assert board_win_p1.scores[1] == 0 and board_win_p1.scores[2] == 0
    assert board_win_p2.scores[1] == 0 and board_win_p2.scores[2] == 0
    assert board_draw.scores[1] == 0 and board_draw.scores[2] == 0

    # Check Win Player 1 (Turn Player 1)
    assert not board_win_p1.is_game_over()
    assert not board_win_p1.game_finished
    assert board_win_p1.get_winner() is None

    board_win_p1.move(0, 1, Orientation.HORIZONTAL)
    board_win_p1.move(0, 0, Orientation.HORIZONTAL)
    board_win_p1.move(1, 1, Orientation.HORIZONTAL)

    assert board_win_p1.is_game_over()
    assert board_win_p1.game_finished
    assert board_win_p1.get_winner() == 1

    # Check Win Player 2 (Turn Player 1)
    assert not board_win_p2.is_game_over()
    assert board_win_p2.get_winner() is None

    board_win_p2.move(0, 1, Orientation.HORIZONTAL)  # P1 score
    board_win_p2.move(1, 0, Orientation.HORIZONTAL)  # P1 no score
    board_win_p2.move(1, 1, Orientation.HORIZONTAL)  # P2 double score
    board_win_p2.move(0, 0, Orientation.HORIZONTAL)  # P2 score

    assert board_win_p2.is_game_over()
    assert board_win_p2.get_winner() == 2

    # Check Draw
    assert not board_draw.is_game_over()
    assert board_draw.get_winner() is None

    board_draw.move(0, 1, Orientation.HORIZONTAL)  # P1 score
    board_draw.move(0, 0, Orientation.HORIZONTAL)  # P1 score
    board_draw.move(1, 0, Orientation.HORIZONTAL)  # P1 no score
    board_draw.move(1, 1, Orientation.HORIZONTAL)  # P2 double score

    assert board_draw.is_game_over()
    assert board_draw.get_winner() == "Draw"


def test_game_state_to_json(create_test_board):
    """Test if Game Configuration is correctly mapped to JSON."""
    board = GameBoard(size=2)
    # Check if JSON contains Player Action
    board.move(0, 0, Orientation.HORIZONTAL)  # P1
    board.move(1, 0, Orientation.VERTICAL)  # P2

    json_state = board.to_json()
    assert isinstance(json_state, dict)

    # Check JSON-Fields
    assert "size" in json_state
    assert "finished" in json_state
    assert "current_player" in json_state
    assert "scores" in json_state
    assert "edges" in json_state
    assert "boxes" in json_state

    # Check complex Objects
    assert isinstance(json_state["edges"]["horizontal"], list)
    assert isinstance(json_state["edges"]["vertical"], list)
    assert isinstance(json_state["boxes"], list)

    # Game State
    assert json_state["current_player"] in [1, 2]
    assert sum(json_state["scores"].values()) == 0
    assert not json_state["finished"]

    horizontal_edges = json_state["edges"]["horizontal"]
    vertical_edges = json_state["edges"]["vertical"]
    boxes = json_state["boxes"]

    # Horizontal: size x (size + 1)
    assert len(horizontal_edges) == board.size
    assert all(len(row) == board.size + 1 for row in horizontal_edges)

    # Vertical: (size + 1) x size
    assert len(vertical_edges) == board.size + 1
    assert all(len(row) == board.size for row in vertical_edges)

    # Check Player Action
    assert horizontal_edges[0][0] == 1
    for x, row in enumerate(horizontal_edges):
        for y, val in enumerate(row):
            if not (x, y) == (0, 0):
                assert val == 0, "Hor. Edge occupied."

    assert vertical_edges[1][0] == 2
    for x, row in enumerate(vertical_edges):
        for y, val in enumerate(row):
            if not (x, y) == (1, 0):
                assert val == 0, "Ver. Edge occupied."

    # Box (0, 0) should have 2 open Edges. (1, 0) -> 3
    assert boxes[0][0] == -2
    assert boxes[1][0] == -3
    for x in range(board.size):
        for y in range(board.size):
            if not (x, y) in [(0, 0), (1, 0)]:
                assert boxes[x][y] == -4


def test_game_parse_enum():
    """Test if String Input is mapped to Enum."""
    orientation_enum = Orientation.VERTICAL

    orientation_str_lower = "horizontal"
    orientation_str_upper = "HORIZONTAL"
    orientation_str_mixed = "Horizontal"

    orientation_str_vert = "vertical"

    orientation_invalid_value = "invalid"

    orientation_invalid_type: int = 0

    assert parse_orientation(orientation=orientation_enum) == Orientation.VERTICAL

    assert (
        parse_orientation(orientation=orientation_str_lower) == Orientation.HORIZONTAL
    )
    assert (
        parse_orientation(orientation=orientation_str_upper) == Orientation.HORIZONTAL
    )
    assert (
        parse_orientation(orientation=orientation_str_mixed) == Orientation.HORIZONTAL
    )

    assert parse_orientation(orientation=orientation_str_vert) == Orientation.VERTICAL

    with pytest.raises(ValueError):
        parse_orientation(orientation=orientation_invalid_value)

    with pytest.raises(TypeError):
        parse_orientation(orientation=orientation_invalid_type)
