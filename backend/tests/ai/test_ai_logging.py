"""Test Logging for all 'ai'-packages."""

import logging
import pytest
from unittest.mock import MagicMock, Mock, mock_open, patch

from ai.bots.random_bot import RandomBot
from ai.data.data_generator import DataGenerator
from ai.data.data_storage import DataStorage

generator_logger = logging.getLogger("ai.data.data_generator")
bot_logger = logging.getLogger("ai.bots.random_bot")
storage_logger = logging.getLogger("ai.data.data_storage")


class MockMove:
    """Simulates Move-Objects."""

    def __init__(self, x, y, orientation):
        """Move-Mock Constructor."""
        self.x = x
        self.y = y
        self.orientation = orientation


class TestDataGeneratorLogging:
    """Test Logging for Data-Generator Class."""

    def test_simulate_game_move_rejected_logs_warning(self, caplog):
        """Test if Logging for a rejected Move works."""
        service = MagicMock()
        bot1 = MagicMock()
        bot2 = MagicMock()
        data_gen = DataGenerator(service)

        mock_game = Mock(game_finished=False)
        service.games = {"test_game": mock_game}
        valid_move = MockMove(x=1, y=2, orientation=Mock(name="HORIZONTAL"))
        invalid_move = MockMove(x=0, y=0, orientation=Mock(name="NONE"))

        bot1.move.side_effect = [
            valid_move,
            invalid_move,
        ]

        error_result = {
            "error": "Invalid placement reason.",
            "scores": {},
            "currentPlayer": 1,
        }

        def side_effect_make_move(*args, **kwargs):
            if side_effect_make_move.call_count == 1:
                side_effect_make_move.call_count += 1
                return error_result
            else:
                mock_game.game_finished = True
                return {"error": None, "scores": {}, "currentPlayer": 2}

        side_effect_make_move.call_count = 1
        service.make_move.side_effect = side_effect_make_move
        service.get_state.return_value = {"state": "before", "currentPlayer": 1}

        with caplog.at_level(logging.WARNING, logger=generator_logger.name):
            data_gen.simulate_game("test_game", bot1, bot2, log=True)

        assert "Move rejected: Invalid placement reason." in caplog.text

        # record_tuples[0]: Source, Level, Message
        assert caplog.record_tuples[0] == (
            generator_logger.name,
            logging.WARNING,
            "Move rejected: Invalid placement reason.",
        )

    def test_simulate_multiple_games_logs_info(self, caplog):
        """Test if Log is created after multiple Game-Simulations."""
        service = MagicMock()
        data_gen = DataGenerator(service)
        data_gen.simulate_game = Mock(return_value=[{"state": "final"}])
        n_games = 5

        with caplog.at_level(logging.INFO, logger=generator_logger.name):
            data_gen.simulate_multiple_games(
                n_games, MagicMock(), MagicMock(), log=True
            )

        expected_log_message = f"Simulated {n_games} games."
        assert expected_log_message in caplog.text
        assert caplog.record_tuples[0] == (
            generator_logger.name,
            logging.INFO,
            expected_log_message,
        )


class TestRandomBotLogging:
    """Test Logging for Random Bot Class."""

    def test_random_bot_no_moves_logs_warning(self, caplog):
        """Test if Log is created for 'No possible Moves available'."""
        random_bot: RandomBot = RandomBot(2)

        for position in random_bot.positions:
            position.available = False

        with pytest.raises(RuntimeError):
            with caplog.at_level(logging.WARNING, logger=bot_logger.name):
                random_bot._select_move(log_move=True)

        expected_log_message = "No possible Moves available."
        assert expected_log_message in caplog.text
        assert caplog.record_tuples[0] == (
            bot_logger.name,
            logging.WARNING,
            expected_log_message,
        )

    def test_random_bot_move_logs_info(self, caplog):
        """Test Move Logging."""
        bot = RandomBot(2)

        with caplog.at_level(logging.INFO, logger=bot_logger.name):
            move = bot._select_move(log_move=True)

        expected = (
            f"RandomBot move: x={move.x}, y={move.y}, orientation={move.orientation}"
        )
        assert caplog.record_tuples[0] == (
            bot_logger.name,
            logging.INFO,
            expected,
        )


class TestDataStorageLogging:
    """Test Data-Storage Logging."""

    def test_datastorage_save_to_json_logs_info(self, caplog, tmp_path):
        """Test if Saving JSON-Data creates Log Entries."""
        storage = DataStorage(log=True)
        mock_file_path = str(tmp_path / "training_data.json")

        # patch os-Operations and json.dump to simulate Data Access
        with patch("os.path.join", side_effect=lambda *args: mock_file_path), patch(
            "os.makedirs"
        ), patch("builtins.open", mock_open()) as mock_file, patch(
            "json.dump"
        ) as mock_json_save:

            # create empty Data File
            with caplog.at_level(logging.INFO, logger=storage_logger.name):
                storage.save_to_json({}, filename="training_data.json")

            expected = f"Saved JSON data to {mock_file_path}"

            assert caplog.record_tuples[0] == (
                storage_logger.name,
                logging.INFO,
                expected,
            )

            assert mock_file.called
            assert mock_json_save.called

    def test_datastorage_load_json_logs_info(self, caplog, tmp_path):
        """Test if Loading JSON-Data creates Log Entries."""
        storage = DataStorage(log=True)
        mock_file_path = str(tmp_path / "training_data.json")
        read_data = '{"key": "value"}'

        # patch os- and storage Operations
        with patch("os.path.join", side_effect=lambda *args: mock_file_path), patch(
            "os.path.exists", return_value=True
        ), patch("builtins.open", mock_open(read_data=read_data)) as mock_file, patch(
            "json.load", return_value={"key": "value"}
        ) as mock_load:

            with caplog.at_level(logging.INFO, logger=storage_logger.name):
                storage.load_from_json(filename="training_data.json")

            expected = f"Loaded JSON data from {mock_file_path}"
            assert caplog.record_tuples[0] == (
                storage_logger.name,
                logging.INFO,
                expected,
            )
            assert mock_file.called
            assert mock_load.called

    def test_datastorage_save_pt_logs_info(self, caplog, tmp_path):
        """Test if Saving .PT-Data creates Log Entries."""
        storage = DataStorage(log=True)
        mock_file_path = str(tmp_path / "training_data.pt")

        # patch torch.save
        with patch("os.makedirs"), patch(
            "os.path.join", side_effect=lambda *args: mock_file_path
        ), patch("ai.data.data_storage.torch.save") as mock_save:

            with caplog.at_level(logging.INFO, logger=storage_logger.name):
                storage.save_to_pt(data="data_tensor", filename="training_data.pt")

            expected = f"Saved PT data to {mock_file_path}"

            assert caplog.record_tuples[0] == (
                storage_logger.name,
                logging.INFO,
                expected,
            )
            assert mock_save.called

    def test_datastorage_load_pt_logs_info(self, caplog, tmp_path):
        """Test if Loading .PT-Data creates Log Entries."""
        storage = DataStorage(log=True)
        mock_file_path = str(tmp_path / "training_data.pt")

        # patch torch.load
        with patch("os.path.exists", return_value=True), patch(
            "os.path.join", side_effect=lambda *args: mock_file_path
        ), patch(
            "ai.data.data_storage.torch.load", return_value="loaded_tensor"
        ) as mock_load:

            with caplog.at_level(logging.INFO, logger=storage_logger.name):
                storage.load_from_pt(filename="training_data.pt")

            expected = f"Loaded PT data from {mock_file_path}"

            assert caplog.record_tuples[0] == (
                storage_logger.name,
                logging.INFO,
                expected,
            )
            assert mock_load.called

    def test_datastorage_print_summary_logs_info(self, caplog):
        """Test if Data-Summary creates a Log Entry."""
        storage = DataStorage()
        fake_data = {
            "game1": [
                {
                    "move": {
                        "scores": [10, 0],
                        "x": 1,
                        "y": 1,
                        "orientation": "HORIZONTAL",
                    }
                }
            ]
        }

        with caplog.at_level(logging.INFO, logger=storage_logger.name):
            storage.print_training_data_summary(fake_data)

        expected = "Write Data Summary."

        assert caplog.record_tuples[0] == (
            storage_logger.name,
            logging.INFO,
            expected,
        )
