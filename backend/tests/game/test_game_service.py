"""Test Class for Service-Tests."""

from unittest.mock import patch
import pytest
from backend.game.position import Position
from backend.game.game_board import Orientation
from backend.game.game_service import GameService

from backend.game.errors import (
    ERROR_BOT_NOT_SET,
    ERROR_EDGE_TAKEN,
    ERROR_GAME_OVER,
    ERROR_INVALID_ORIENTATION_TYPE,
    ERROR_NOT_YOUR_TURN,
    ERROR_OUT_OF_BOUNDS,
    ERROR_GAME_EXISTS,
    ERROR_GAME_NOT_FOUND,
)
from backend.game.game_state import GameState

game_id = "1"


@pytest.fixture
def services():
    """Creates a new Game-Service Object with 2x2 Board."""
    with patch(
        "backend.game.game_service.bot_service", autospec=True
    ) as mock_bot_service:
        game_service = GameService()
        game_service.create_game(game_id, size=2)
        yield game_service, mock_bot_service

        # Removes Bot in BotService
        game_service.delete_game(game_id)


def test_initial_state(services):
    """Test new Game initialization."""
    service, _ = services
    # Default Game exists
    assert game_id in service.games

    assert service.create_game(game_id="1", size=12) == ERROR_GAME_EXISTS
    assert service.get_state(game_id="999") == ERROR_GAME_NOT_FOUND

    state = service.get_state(game_id)

    # Check Structure
    assert isinstance(state, dict)
    assert state["size"] == 2
    assert "edges" in state
    assert "boxes" in state
    assert state["scores"] == {1: 0, 2: 0}
    assert state["finished"] is False
    assert state["current_player"] == 1

    # All Edges free
    assert all(val == 0 for row in state["edges"]["horizontal"] for val in row)
    assert all(val == 0 for row in state["edges"]["vertical"] for val in row)

    # All Boxes empty
    assert all(val == -4 for row in state["boxes"] for val in row)


def test_make_move_changes_state(services):
    """Test if Player Action changes Board Configuration."""
    # Create a closed box and check Board (action: player_id, x, y, orientation)
    service, _ = services
    actions = [
        (1, 0, 0, Orientation.HORIZONTAL),  # P1
        (2, 0, 1, Orientation.HORIZONTAL),  # P2
        (1, 0, 0, Orientation.VERTICAL),  # P1
        (2, 1, 0, Orientation.VERTICAL),  # P2 scores (0, 0)
    ]

    for action in actions:
        service.make_move(game_id, *action)

    result = service.get_state(game_id)

    assert result["current_player"] == 2
    assert result["edges"]["horizontal"][0][0] == 1
    assert result["edges"]["horizontal"][0][1] == 2
    assert result["edges"]["vertical"][0][0] == 1
    assert result["edges"]["vertical"][1][0] == 2
    assert result["boxes"][0][0] == 2
    assert result["finished"] is False
    assert result["scores"] == {1: 0, 2: 1}


def test_restart_game_resets_everything(services):
    """Test if Restart Call empties everything."""
    service, _ = services
    service.make_move(game_id, 1, 0, 0, Orientation.HORIZONTAL)
    state_before = service.get_state(game_id)

    new_state = service.restart_game(game_id)

    assert new_state["current_player"] == 1
    assert new_state["scores"] == {1: 0, 2: 0}
    # Check Board is empty
    assert all(val == 0 for row in new_state["edges"]["horizontal"] for val in row)
    assert all(val == 0 for row in new_state["edges"]["vertical"] for val in row)
    assert state_before != new_state


def test_restart_game_invalid_id_returns_error(services):
    """Test if an error-message is returned for an unknown game."""
    service, _ = services
    invalid_game_id = "invalid_game_id"

    assert invalid_game_id not in service.games
    error_message = service.restart_game(invalid_game_id)

    assert "error" in error_message
    assert error_message["error"] == ERROR_GAME_NOT_FOUND["error"]


def test_game_over_detection(services):
    """Test if an Action triggers Game-Over Flag."""
    service, _ = services
    # Moves in 2x2 for Draw, all Edges filled
    moves = [
        (1, 0, 0, Orientation.HORIZONTAL),  # Player 1
        (2, 0, 0, Orientation.VERTICAL),  # Player 2
        (1, 1, 0, Orientation.HORIZONTAL),  # Player 1
        (2, 0, 1, Orientation.VERTICAL),  # Player 2
        (1, 0, 1, Orientation.HORIZONTAL),  # Player 1
        (2, 1, 0, Orientation.VERTICAL),  # Player 2 (score)
        (2, 1, 1, Orientation.HORIZONTAL),  # Player 2
        (1, 1, 1, Orientation.VERTICAL),  # Player 1
        (2, 0, 2, Orientation.HORIZONTAL),  # Player 2 (score)
        (2, 2, 1, Orientation.VERTICAL),  # Player 2
        (1, 1, 2, Orientation.HORIZONTAL),  # Player 1 (score)
        (1, 2, 0, Orientation.VERTICAL),  # Player 1 (score)
    ]

    for p, x, y, o in moves:
        service.make_move(game_id, p, x, y, o)

    assert isinstance(service.is_game_over(game_id), bool)
    assert service.is_game_over(game_id)
    assert service.get_state(game_id)["finished"] is True
    assert service.get_winner(game_id) == "Draw"

    # Check Additional Moves after Game End
    prev_state = service.get_state(game_id).copy()
    assert (
        service.make_move(game_id, 2, 0, 0, Orientation.HORIZONTAL) == ERROR_GAME_OVER
    )
    assert service.get_state(game_id) == prev_state


def test_invalid_move(services):
    """Test if illegal moves (duplicate edges) returns an Error-Message."""
    service, _ = services
    service.make_move(game_id, 1, 0, 0, Orientation.HORIZONTAL)

    with pytest.raises(ValueError, match=ERROR_EDGE_TAKEN["error"]):
        service.make_move(game_id, 2, 0, 0, Orientation.HORIZONTAL)

    # Test-Board is smaller than 5x5
    with pytest.raises(ValueError, match=ERROR_OUT_OF_BOUNDS["error"]):
        service.make_move(game_id, 2, 5, 5, Orientation.HORIZONTAL)

    with pytest.raises(TypeError, match=ERROR_INVALID_ORIENTATION_TYPE["error"]):
        service.make_move(game_id, 2, 0, 0, None)


def test_move_returns_error_message(services):
    """Test if error message is returned for different cases."""
    service, _ = services

    # game not found
    invalid_id = "invalid_game_id"
    assert invalid_id not in service.games

    msg_game_not_found = service.make_move(invalid_id, 1, 1, 1, Orientation.HORIZONTAL)
    assert "error" in msg_game_not_found
    assert msg_game_not_found["error"] == ERROR_GAME_NOT_FOUND["error"]

    # not your turn
    wrong_turn_id = "new_game_wrong_turn"
    service.create_game(game_id=wrong_turn_id, starting_player=2)
    msg_not_your_turn = service.make_move(
        wrong_turn_id, 1, 1, 1, Orientation.HORIZONTAL
    )
    assert "error" in msg_not_your_turn
    assert msg_not_your_turn["error"] == ERROR_NOT_YOUR_TURN["error"]

    # game over
    game_over_id = "new_game_finished"
    service.create_game(game_over_id)
    service.games[game_over_id].game_finished = True

    msg_game_over = service.make_move(game_over_id, 1, 1, 1, Orientation.HORIZONTAL)
    assert "error" in msg_game_over
    assert msg_game_over["error"] == ERROR_GAME_OVER["error"]


def test_new_game_is_available(services):
    """Test if Game Creation works for multiple Games."""
    service, _ = services
    service.create_game("111", size=4)
    service.create_game("222", size=6)
    service.create_game("333", size=5)

    data_game_1 = service.get_state("111")
    data_game_2 = service.get_state("222")
    data_game_3 = service.get_state("333")

    assert data_game_1["size"] == 4
    assert data_game_2["size"] == 6
    assert data_game_3["size"] == 5


def test_new_game_registers_bot(services):
    """Test if create_game() uses BotService to register the given bot model."""
    service, bot_service = services
    new_game_id = "new_game_id"
    bot_model = "random"

    service.create_game(new_game_id, bot_model=bot_model)
    bot_service.register_bot.assert_called_once()


def test_make_bot_move(services):
    """Test GameService.make_bot_move handles bot logic and state updates."""
    service, mock_bot_service = services

    bot_id = 1
    bot_model_name = "test_bot"

    board = service.games[game_id]
    board.bot_model = bot_model_name
    board.bot_id = bot_id

    expected_move = Position(x=1, y=1, orientation=Orientation.VERTICAL, available=True)

    mock_bot_service.game_state_required.return_value = True
    mock_bot_service.get_move.return_value = expected_move

    initial_current_player = board.current_player
    result_move = service.make_bot_move(game_id)

    # Move was executed and state updated
    assert result_move is expected_move
    assert board.current_player != initial_current_player
    assert board.edges_vertical[1][1] == bot_id

    # Test Game State Check
    mock_bot_service.game_state_required.assert_called_with(bot_model_name)

    # Test wrong Turn
    result_error = service.make_bot_move(game_id)
    assert result_error == ERROR_NOT_YOUR_TURN

    # Test Bot not set
    service.restart_game(game_id)
    board.bot_model = None
    board.bot_id = None

    # Create new Game without bot set
    game_no_bot = "no_bot"
    service.create_game(game_id=game_no_bot)
    # Make Move to switch Turns (bot.pos = 2)
    service.make_move(
        game_id=game_no_bot, player_id=1, x=0, y=0, orientation=Orientation.HORIZONTAL
    )
    result_error = service.make_bot_move(game_no_bot)
    assert result_error == ERROR_BOT_NOT_SET

    # bot move for invalid game id
    invalid_id = "invalid_game_id"
    assert invalid_id not in service.games
    result_error_no_game = service.make_bot_move(invalid_id)
    assert "error" in result_error_no_game
    assert result_error_no_game["error"] == ERROR_GAME_NOT_FOUND["error"]


def test_make_move_updates_bot(services):
    """Test if moves are passed to the BotService."""
    service, bot_service = services

    bot_game_id = "new_game_bot"
    service.create_game(bot_game_id, bot_model="random")

    service.make_move(bot_game_id, 1, 1, 1, Orientation.HORIZONTAL)

    bot_service.update_possible_moves.assert_called_once()


def test_get_state_object(services):
    """Test if GameState is returned for given game-id."""
    service, _ = services
    # should work for game set in fixture
    game_state = service.get_state_object(game_id)
    assert isinstance(game_state, GameState)

    # should return error-message for unknown game
    invalid_id = "invalid_game_id"
    error_message = service.get_state_object(invalid_id)
    assert isinstance(error_message, dict)
    assert "error" in error_message
    assert error_message["error"] == ERROR_GAME_NOT_FOUND["error"]
