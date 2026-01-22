"""Test Class for Data Generator."""

import sys

from unittest.mock import MagicMock, Mock, patch
from ai.bots.move import Move
from game.game_board import Orientation
from ai.data.data_generator import DataGenerator, main


def test_simulate_game_standard():
    """Test Game Simulation resets Bots and returns Game-Data after Simulation."""
    # Create GameService-Mock
    service = MagicMock()
    service.games = {"game_1": MagicMock(game_finished=True)}

    b1 = MagicMock()
    b2 = MagicMock()

    data_generator = DataGenerator(service, board_size=4)

    data = data_generator.simulate_game("game_1", b1, b2)

    # Check Bot reset
    b1.reset.assert_called_once()
    b2.reset.assert_called_once()

    assert isinstance(data, list)


def test_new_game_creation():
    """Test if new Game is created."""
    # Setup Mocks
    service = MagicMock()
    bot1 = MagicMock()
    bot2 = MagicMock()

    mock_game = Mock(game_finished=True)
    service.games = {}

    # simulate Game Creation
    def create_game_side_effect(game_id, **kwargs):
        service.games[game_id] = mock_game

    service.create_game.side_effect = create_game_side_effect

    game_id = "new_game"
    board_size = 3

    data_generator = DataGenerator(service, board_size=board_size)
    data_generator.simulate_game(game_id, bot1, bot2)

    # Check if new Game is created (instead of reset)
    service.create_game.assert_called_once_with(
        game_id, size=data_generator.board_size, starting_player=1
    )
    service.restart_game.assert_not_called()

    # Game-Service contains new game
    assert service.games[game_id] == mock_game
    # Moves not allowed (game finished)
    service.make_move.assert_not_called()


def test_invalid_move_rejected_and_updated():
    """Test handling of invalid Move Actions."""
    # Setup Mocks
    service = MagicMock()
    data_generator = DataGenerator(service)

    mock_game = Mock(game_finished=False)
    service.games = {"test_game": mock_game}

    bot1 = MagicMock()
    bot2 = MagicMock()

    # Setup moves, second should raise error
    move_valid = Move(x=1, y=2, orientation=Orientation.HORIZONTAL)
    move_invalid = Move(x=10, y=10, orientation=Orientation.VERTICAL)

    bot1.move.side_effect = [move_valid, move_invalid]

    error_result = {"error": "Invalid placement"}

    def side_effect_make_move(*args, **kwargs):
        # Second Call raises Error
        if side_effect_make_move.call_count == 0:
            side_effect_make_move.call_count += 1
            return error_result
        else:
            mock_game.game_finished = True
            return {
                "scores": {},
                "current_player": 2,
            }

    side_effect_make_move.call_count = 0
    service.make_move.side_effect = side_effect_make_move

    data = data_generator.simulate_game("test_game", bot1, bot2)

    bot1.update.assert_any_call(move_valid.x, move_valid.y, move_valid.orientation)

    assert len(data) == 1


def test_simulate_multiple_games():
    """Test if Game-Data of multiple Simulations is returned."""
    service = MagicMock()
    data_generator = DataGenerator(service)

    # Mock Return Value of single Game-Simulation
    data_generator.simulate_game = MagicMock(return_value=["game_mock"])

    data = data_generator.simulate_multiple_games(
        n_games=3, bot1=MagicMock(), bot2=MagicMock(), prefix="test_game"
    )

    # Data contains 3 Simulations
    assert len(data) == 3

    # Check Prefix and Indexing works
    assert "test_game_1" in data
    assert "test_game_3" in data
    data_generator.simulate_game.assert_called()


@patch("ai.data.data_generator.DataStorage")
def test_main_view_parameter(storage_mock):
    """Terminal Parameter 'view' loads and prints data."""
    storage_instance = storage_mock.return_value
    storage_instance.load_from_pt.return_value = {"dummy": 1}

    test_args = ["prog", "--view", "5"]
    with patch.object(sys, "argv", test_args):
        main()

    # Storage Functions have been called
    storage_instance.load_from_pt.assert_called_once()
    storage_instance.print_training_data_summary.assert_called_once()


@patch("ai.bots.bot_service.BOT_MODEL")
@patch("ai.data.data_generator.DataGenerator")
def test_main_runs_simulation(generator_mock: Mock, bot_classes_mock: Mock):
    """Test if Terminal Parameter is processed correctly."""
    generator_object = generator_mock.return_value
    generator_object.simulate_multiple_games.return_value = {}

    MockBot = Mock()
    bot_classes_mock.get.side_effect = [MockBot, MockBot]

    # Simulate Terminal Input
    test_args = ["prog", "--games", "10", "--size", "7"]

    with patch.object(sys, "argv", test_args):
        main()

    # RandomBot is used (default)
    bot_classes_mock.get.assert_called()

    # Check if simulate_multiple_games is called
    generator_object.simulate_multiple_games.assert_called_once()


@patch("ai.data.data_generator.DataStorage")
@patch("ai.data.data_generator.DataGenerator")
def test_main_json_save(generator_mock, storage_mock):
    """Test if Json Data storage works."""
    generator_object = generator_mock.return_value
    generator_object.simulate_multiple_games.return_value = {
        "game_1": ["data_1"],
        "game_2": ["data_2"],
    }
    storage_object = storage_mock.return_value

    test_args = ["prog", "--json", "1", "--log"]
    with patch.object(sys, "argv", test_args):
        main()

    # Check if Storage Function is called, .pt is created by default
    storage_object.save_to_json.assert_called_once()
    storage_object.save_to_pt.assert_called_once()


@patch("ai.data.data_generator.DataStorage")
@patch("ai.data.data_generator.DataGenerator")
def test_main_prohibit_pt_save(generator_mock, storage_mock):
    """Test if .pt-File is not created (no-pt Parameter used)."""
    generator_object = generator_mock.return_value
    generator_object.simulate_multiple_games.return_value = {"game": "data"}

    test_args = ["prog", "--no-pt"]
    with patch.object(sys, "argv", test_args):
        main()

    storage_mock.return_value.save_to_pt.assert_not_called()


@patch("ai.data.data_generator.DataGenerator")
def test_main_invalid_bot(generator_mock):
    """Test if .pt-File is not created (no-pt Parameter used)."""
    generator_object = generator_mock.return_value
    generator_object.simulate_multiple_games.return_value = {"game": "data"}

    test_args = ["prog", "--bot1", "invalid"]
    with patch.object(sys, "argv", test_args):
        main()

    # Process ended after Bot-Creation
    generator_object.simulate_multiple_games.assert_not_called()

@patch("ai.data.data_generator.os.path.exists", return_value=False)
@patch("ai.data.data_generator.DataGenerator")
def test_main_merge_no_file_exists(generator_mock, mock_makedirs):
    """Test if process is aborted when no file to merge exists."""
    generator_object = generator_mock.return_value

    test_args = ["prog", "--bot1", "random", "--merge"]
    with patch.object(sys, "argv", test_args):
        main()

    generator_object.simulate_multiple_games.assert_not_called()
