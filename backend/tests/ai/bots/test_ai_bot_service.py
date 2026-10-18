"""Test Class for the Bot Service."""

from unittest.mock import MagicMock, patch
import pytest

from backend.ai.agents.base_agent import BaseAgent
from backend.ai.agents.bot_service import ACTIVE_BOTS, BotService

from backend.ai.agents.bot_service import BOT_MODEL
from backend.ai.agents.ffn_agent import FFNAgent
from backend.game.position import Position
from backend.ai.agents.random_agent import RandomAgent
from backend.ai.agents.heuristic_agent import HeuristicAgent
from backend.game.game_board import Orientation
from backend.game.game_state import GameState


@pytest.fixture
def create_bot_service():
    """Returns a new BotService instance."""
    return BotService()


@pytest.fixture(autouse=True)
def cleanup_active_bots():
    """Cleanup ACTIVE_BOTS after each test."""
    ACTIVE_BOTS.clear()
    yield
    ACTIVE_BOTS.clear()


def test_get_bot_model(create_bot_service):
    """Test if get_bot_model returns the correct Bot class."""
    service = create_bot_service
    models = service.get_bot_models()

    # Check BOT_MODEL dict
    assert models == set(BOT_MODEL.keys())
    assert all(isinstance(model, str) for model in models)

    assert service.get_bot_model("random") is RandomAgent
    assert service.get_bot_model("ffn") is FFNAgent
    assert issubclass(service.get_bot_model("rule"), BaseAgent)


def test_get_bot_model_invalid_model(create_bot_service):
    """Test ValueError is raised for an invalid bot model name."""
    service = create_bot_service

    with pytest.raises(ValueError, match="Bot Model not found"):
        service.get_bot_model("invalid")


def test_is_nn_bot_string_input(create_bot_service):
    """Test is_nn_bot with model name (string) input."""
    service = create_bot_service

    # NN Bots
    assert service.game_state_required("ffn") is True
    assert service.game_state_required("pvn") is True

    # non-NN Bots
    assert service.game_state_required("random") is False
    assert service.game_state_required("rule") is False


def test_is_nn_bot_object_input(create_bot_service):
    """Test is_nn_bot with a mocked NN Bot object."""
    service = create_bot_service

    mock_ffn_agent = MagicMock(spec=FFNAgent)
    mock_ffn_agent.name.return_value = FFNAgent.BOT_NAME
    mock_ffn_agent.game_state_required.return_value = True
    mock_random_bot = MagicMock(spec=RandomAgent)
    mock_random_bot.name.return_value = RandomAgent.BOT_NAME
    mock_random_bot.game_state_required.return_value = False

    assert service.game_state_required(mock_ffn_agent) is True
    assert service.game_state_required(mock_random_bot) is False


def test_register_bot(create_bot_service):
    """Test successful registration of a bot."""
    service = create_bot_service
    game_id = "game_1"

    service.register_bot(game_id, size=4, bot_model="random")

    assert game_id in ACTIVE_BOTS
    assert isinstance(ACTIVE_BOTS[game_id], RandomAgent)
    assert service.get_bot(game_id) is ACTIVE_BOTS[game_id]


def test_register_bot_bot_already_exists(create_bot_service):
    """Test ValueError is raised on duplicate registration."""
    service = create_bot_service
    game_id = "game_duplicate"
    service.register_bot(game_id, size=2, bot_model="rule")

    with pytest.raises(ValueError, match="already registered"):
        service.register_bot(game_id, size=2, bot_model="random")


def test_get_bot_not_found(create_bot_service):
    """Test ValueError is raised when trying to get an unregistered bot."""
    service = create_bot_service

    with pytest.raises(ValueError, match="No Bot-Registration found"):
        service.get_bot("non_existent_game")


def test_delete_bot_successful(create_bot_service):
    """Test successful deletion of a registered bot."""
    service = create_bot_service
    game_id = "game_to_delete"
    service.register_bot(game_id, size=2, bot_model="random")

    result = service.delete_bot(game_id)

    assert game_id not in ACTIVE_BOTS
    assert f"Deleted Bot: {RandomAgent.BOT_NAME}" in result
    with pytest.raises(ValueError):
        service.get_bot(game_id)


def test_delete_bot_not_found(create_bot_service):
    """Test ValueError is raised when trying to delete an unknown bot."""
    service = create_bot_service

    with pytest.raises(ValueError, match="No Bot found for Game-ID invalid_id"):
        service.delete_bot("invalid_id")


@patch("backend.ai.agents.bot_service.BotService.get_bot")
@patch("backend.ai.agents.bot_service.BotService.game_state_required", return_value=False)
def test_get_move_non_nn_bot(MockIsNN, MockGetBot, create_bot_service):
    """Test get_move for a non-NN bot (no GameState required)."""
    service = create_bot_service
    game_id = "game_rule"

    mock_bot = MagicMock(spec=HeuristicAgent, name="rule")
    expected_move = Position(x=0, y=0, orientation=Orientation.HORIZONTAL, available=True)
    mock_bot.move.return_value = expected_move
    MockGetBot.return_value = mock_bot

    pred_move = service.get_move(game_id, game_state=None)

    assert pred_move is expected_move
    mock_bot.move.assert_called_once()


@patch("backend.ai.agents.bot_service.BotService.get_bot")
@patch("backend.ai.agents.bot_service.BotService.game_state_required", return_value=True)
def test_get_move_nn_bot_with_state(MockIsNN, MockGetBot, create_bot_service):
    """Test get_move for an NN bot with GameState (should call update_state)."""
    service = create_bot_service
    game_id = "game_nn"

    mock_bot = MagicMock(spec=FFNAgent, name="ffn-bot")
    game_state_mock = MagicMock(spec=GameState)
    expected_move = Position(x=1, y=1, orientation=Orientation.VERTICAL, available=True)
    mock_bot.move.return_value = expected_move
    MockGetBot.return_value = mock_bot

    pred_move = service.get_move(game_id, game_state_mock)

    assert pred_move is expected_move

    # Check state was updated
    mock_bot.update_state.assert_called_once_with(game_state_mock)
    mock_bot.move.assert_called_once()


@patch("backend.ai.agents.bot_service.BotService.get_bot")
@patch("backend.ai.agents.bot_service.BotService.game_state_required", return_value=True)
def test_get_move_nn_bot_raises_without_state(MockIsNN, MockGetBot, create_bot_service):
    """Test get_move for an NN bot without GameState (should raise error)."""
    service = create_bot_service
    game_id = "game_nn"

    mock_bot = MagicMock(spec=FFNAgent, name="ffn-bot")
    mock_bot.name.return_value = "ffn-bot"
    MockGetBot.return_value = mock_bot

    with pytest.raises(ValueError, match="NN Bot 'ffn-bot' needs GameState"):
        service.get_move(game_id, game_state=None)
