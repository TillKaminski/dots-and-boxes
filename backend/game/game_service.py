"""Class that handles Communication between APIs and Game Logic."""

from .game_board import GameBoard, Orientation
from .errors import (
    ERROR_EDGE_TAKEN,
    ERROR_GAME_OVER,
    ERROR_OUT_OF_BOUNDS,
    ERROR_INVALID_ORIENTATION,
    ERROR_GAME_EXISTS,
    ERROR_GAME_NOT_FOUND
)


class GameService:
    """Game-Service Object that handles State Management and Communication."""

    def __init__(self):
        """Implement Constructor."""
        self.games: dict[str, GameBoard] = {}

    def create_game(self, game_id: str, size: int = 3):
        """Creates a new Game Session."""
        if game_id in self.games:
            return ERROR_GAME_EXISTS
        self.games[game_id] = GameBoard(size=size)
        return self.get_state(game_id)

    def make_move(self, game_id: str, x: int, y: int, orientation: Orientation):
        """Handle Move-Logic."""
        board = self._get_game(game_id)
        if board.is_game_over():
            return ERROR_GAME_OVER
        board.move(x, y, orientation)
        return self.get_state(game_id)

    def get_state(self, game_id: str):
        """Return JSON-Object of Game-State (or Error Message)."""
        game = self._get_game(game_id)
        if isinstance(game, GameBoard):
            return game.to_json()
        return game

    def restart_game(self, game_id: str):
        """Restart current Game-Session."""
        board = self._get_game(game_id)
        size = board.size
        self.games[game_id] = GameBoard(size=size) 
        return self.get_state(game_id)

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
