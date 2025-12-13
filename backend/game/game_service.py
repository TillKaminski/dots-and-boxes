"""Class that handles Communication between APIs and Game Logic."""

from ai.bots.bot_service import BotService
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
        if board.is_game_over() or board.game_finished:
            return ERROR_GAME_OVER
        if board.current_player != player_id:
            return ERROR_NOT_YOUR_TURN
        board.move(x, y, orientation)
        return self.get_state(game_id)

    def make_bot_move(self, game_id: str):
        """Redirects Request to BotService to perform a Bot Move."""
        board = self._get_game(game_id)
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

        return move

    def get_state(self, game_id: str):
        """Return JSON-Object of Game-State (or Error Message)."""
        game = self._get_game(game_id)
        if isinstance(game, GameBoard):
            return game.to_json()
        return game

    def get_state_object(self, game_id: str):
        """Return Game-State Object."""
        game: GameBoard = self._get_game(game_id)
        return game.get_state_object()

    def restart_game(self, game_id: str):
        """Restart current Game-Session."""
        board = self._get_game(game_id)
        if isinstance(board, GameBoard):
            size = board.size
            bot = board.bot_model
            if bot:
                bot_service.delete_bot(game_id)
            self.games[game_id] = GameBoard(size=size, bot_model=bot)
            if bot:
                bot_service.register_bot(game_id, size, bot)
            return self.get_state(game_id)
        return board

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
