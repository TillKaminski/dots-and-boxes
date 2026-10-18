"""Unit-Tests for the FeedForward Bot."""

import pytest
from unittest.mock import patch, MagicMock
import torch

from backend.ai.bots.ffn_bot import FFNBot

from backend.game.game_state import GameState

BOT_SIZE = 4
MOCK_INPUT_SIZE = 10
MOCK_OUTPUT_SIZE = BOT_SIZE * (BOT_SIZE + 1) * 2  # 2*(3)*2 = 12 für size=2
MOCK_MODEL_PATH = "dummy/path/model.pt"


@pytest.fixture
def state_mock():
    """Creates a Mock for the GameState."""
    mock_state = MagicMock(spec=GameState)

    mock_board = MagicMock()
    mock_board.size = BOT_SIZE
    mock_state.board = mock_board

    return mock_state


@pytest.fixture  # (autouse=True)
@patch("backend.ai.bots.ffn_bot.os.path.join", return_value=MOCK_MODEL_PATH)
@patch("backend.ai.bots.ffn_bot.os.path.exists", return_value=True)
@patch("backend.ai.bots.ffn_bot.torch.load")
@patch("backend.ai.bots.ffn_bot.FeedForwardNet")
@patch("backend.ai.bots.ffn_bot.ModelConfig")
@patch("backend.ai.bots.ffn_bot.DeploymentConfig")
def ffn_bot_mock(
    MockDeploymentConfig, MockModelConfig, MockFFN, MockLoad, MockExists, MockJoin
):
    """Creates a Mock for the FFNBot (and Mocks for Dependencies)."""
    # Mock Configs
    MockModelConfig.OUTPUT_SIZE = MOCK_OUTPUT_SIZE
    MockModelConfig.INPUT_SIZE = MOCK_INPUT_SIZE
    MockModelConfig.HIDDEN_LAYERS = [5]
    MockDeploymentConfig.MODEL_PATH = MOCK_MODEL_PATH

    bot = FFNBot(size=BOT_SIZE)
    bot.model = MockFFN.return_value

    return bot


def test_ffn_bot_initialization(ffn_bot_mock):
    """Tests Initialization Model Loading."""
    bot = ffn_bot_mock

    assert bot.size == BOT_SIZE
    assert len(bot.positions) == MOCK_OUTPUT_SIZE

    assert isinstance(bot.model, MagicMock)


def test_ffn_bot_load_model_not_found(ffn_bot_mock):
    """Test, if Logging works for 'Model not found'."""
    with patch("backend.ai.bots.ffn_bot.os.path.exists", return_value=False):
        with patch("backend.ai.bots.ffn_bot.logger.warning") as mock_logger:
            bot = ffn_bot_mock
            bot._load_model()
            mock_logger.assert_called_once()
            assert "Model file not found" in mock_logger.call_args[0][0]


def test_ffn_bot_reset(ffn_bot_mock):
    """Test reset() makes all positions available."""
    bot = ffn_bot_mock

    for i in range(MOCK_OUTPUT_SIZE - 1):
        bot.positions[i].available = False

    bot.reset()

    for pos in bot.positions:
        assert pos.available

    assert bot._current_state is None


def test_ffn_bot_move_no_state_set(ffn_bot_mock):
    """Test, if move() without a State set raises an Error."""
    bot = ffn_bot_mock
    bot._current_state = None
    with pytest.raises(RuntimeError, match="No Game State set."):
        bot.move()


def test_ffn_bot_move(ffn_bot_mock, state_mock):
    """Test, if move-Method returns a valid Move."""
    bot = ffn_bot_mock
    bot.update_state(state_mock)

    best_index = 7
    mock_output = torch.zeros(MOCK_OUTPUT_SIZE, dtype=torch.float32)
    mock_output[best_index] = 100.0

    mock_model = MagicMock()
    mock_model.return_value = mock_output.unsqueeze(0)
    bot.model = mock_model

    mock_serialize = MagicMock(return_value=torch.ones(MOCK_INPUT_SIZE))
    bot.preprocessor._serialize_state = mock_serialize

    bot.positions[best_index].available = True
    expected_move = bot.positions[best_index]

    move_result = bot.move(log_move=True, return_dictionary=False)

    assert move_result is expected_move
    bot.model.assert_called_once()


def test_ffn_bot_map_index_invalid(ffn_bot_mock):
    """Test, if mapping an invalid Position-Index throws an Error."""
    # Test negative
    with pytest.raises(ValueError):
        ffn_bot_mock._map_index_to_move(-1)
    # Test out of bounds
    with pytest.raises(ValueError):
        ffn_bot_mock._map_index_to_move(1000)


def test_ffn_bot_update_positions(ffn_bot_mock):
    """Test, if Move is unavailable after update()."""
    bot = ffn_bot_mock

    # Chose random Move
    move_to_update = bot.positions[5]
    bot.update(move_to_update.x, move_to_update.y, move_to_update.orientation)

    assert not move_to_update.available


def test_ffn_bot_update_state(ffn_bot_mock, state_mock):
    """Test Updating the internal GameState."""
    bot = ffn_bot_mock
    bot.update_state(state_mock)
    assert bot._current_state is state_mock


def test_ffn_bot_name(ffn_bot_mock):
    """Test, if Name-Method returns the correct Bpt-Name."""
    bot = ffn_bot_mock
    assert bot.name() == FFNBot.BOT_NAME


@patch("backend.ai.bots.ffn_bot.random.random")
def test_ffn_bot_move_epsilon_set(mock_random, ffn_bot_mock, state_mock):
    """Tests if exploration is triggered when random < epsilon."""
    bot = ffn_bot_mock
    bot.update_state(state_mock)

    bot.epsilon = 0.5
    mock_random.return_value = 0.1

    with patch.object(bot, "_get_random_legal_move") as mock_random_move:
        mock_random_move.return_value = bot.positions[0]

        move_result = bot.move()

        mock_random_move.assert_called_once()
        assert move_result == bot.positions[0]


def test_ffn_bot_get_random_legal_move(ffn_bot_mock):
    """Tests if only available moves are selected (for epsilon > 0)."""
    bot = ffn_bot_mock

    for pos in bot.positions:
        pos.available = False

    bot.positions[2].available = True
    bot.positions[5].available = True
    allowed_indices = [2, 5]

    random_move = bot._get_random_legal_move()
    chosen_index = bot.positions.index(random_move)
    assert chosen_index in allowed_indices
    assert random_move.available is True
