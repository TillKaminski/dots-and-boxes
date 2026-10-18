"""Class that handles Communication between APIs and Game Logic."""

from backend.ai.bots.bot_service import BotService
from .game_board import GameBoard, Orientation
from .errors import (
    ERROR_GAME_OVER,
    ERROR_GAME_EXISTS,
    ERROR_GAME_NOT_FOUND,
    ERROR_BOT_NOT_SET,
    ERROR_NOT_YOUR_TURN,
)

bot_service = BotService()


class GameService:
    """Game-Service Object that handles State Management and Communication."""

    def __init__(self):
        """Stores all Game Objects."""
        self.games: dict[str, GameBoard] = {}

    def create_game(
        self,
        game_id: str,
        size: int = 4,
        starting_player: int = 1,
        bot_model: str | None = None,
    ):
        """Creates a new Game Session."""
        if game_id in self.games:
            return ERROR_GAME_EXISTS
        if bot_model:
            if not bot_service.is_bot_size_available(bot_model, size):
                bot_model = "rule"
            bot_service.register_bot(game_id, size, bot_model)
        self.games[game_id] = GameBoard(
            size=size, starting_player=starting_player, bot_model=bot_model
        )
        return self.get_state(game_id)

    def make_move(
        self, game_id: str, player_id: int, x: int, y: int, orientation: Orientation
    ):
        """Handle Move-Logic."""
        board = self._get_game(game_id)
        if isinstance(board, dict):
            return board
        if board.is_game_over() or board.game_finished:
            return ERROR_GAME_OVER
        if board.current_player != player_id:
            return ERROR_NOT_YOUR_TURN
        board.move(x, y, orientation)
        # TODO: Fix for Player vs. Player
        if board.bot_model:
            bot_service.update_possible_moves(game_id, x, y, orientation)
        return self.get_state(game_id)

    def make_bot_move(self, game_id: str):
        """Redirects Request to BotService to perform a Bot Move."""
        board = self._get_game(game_id)
        if isinstance(board, dict):
            return board
        bot_model_name = board.bot_model
        if bot_model_name is None:
            return ERROR_BOT_NOT_SET
        bot_id = board.bot_id
        if bot_id != board.current_player:
            return ERROR_NOT_YOUR_TURN
        # Check Bot Type
        current_state = None
        if bot_service.game_state_required(bot_model_name):
            current_state = board.get_state_object()

        move = bot_service.get_move(game_id=game_id, game_state=current_state)
        board.move(move.x, move.y, move.orientation)

        bot_service.update_possible_moves(game_id, move.x, move.y, move.orientation)

        return move

    def get_state(self, game_id: str):
        """Return JSON-Object of Game-State (or Error Message)."""
        game = self._get_game(game_id)
        if isinstance(game, GameBoard):
            return game.to_json()
        return game

    def get_state_object(self, game_id: str):
        """Return Game-State Object."""
        game = self._get_game(game_id)
        if isinstance(game, dict):
            return game
        return game.get_state_object()

    def restart_game(self, game_id: str, board_size: int = 0, starting_player: int = 1, bot_model: str | None = None):
        """Restart current Game-Session."""
        board = self._get_game(game_id)
        # Check for error
        if isinstance(board, dict):
            return board
        if isinstance(board, GameBoard):
            size = board.size if (board_size == 0) else board_size
            if board.bot_model:
                bot_service.delete_bot(game_id)
            target_bot = bot_model if bot_model is not None else board.bot_model
            if target_bot:
                if not bot_service.is_bot_size_available(target_bot, size):
                    target_bot = "rule"
            self.games[game_id] = GameBoard(
                size=size, bot_model=target_bot, starting_player=starting_player
            )
            if target_bot:
                bot_service.register_bot(game_id, size, target_bot)
            return self.get_state(game_id)

    def delete_game(self, game_id: str):
        """Delete Game-Session by ID."""
        self.games.pop(game_id)
        bot_service.delete_bot(game_id)

    def is_game_over(self, game_id: str):
        """Check if Game is over."""
        return self._get_game(game_id).is_game_over()

    def get_winner(self, game_id: str):
        """Return ID of winning Player."""
        return self._get_game(game_id).get_winner()

    def _get_game(self, game_id: str) -> GameBoard:
        """Find Game by ID."""
        if game_id not in self.games:
            return ERROR_GAME_NOT_FOUND
        return self.games[game_id]
