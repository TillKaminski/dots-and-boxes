"""Class that handles Communication between APIs and Game Logic."""

from .errors import (
    ERROR_EDGE_TAKEN,
    ERROR_GAME_OVER,
    ERROR_OUT_OF_BOUNDS,
    ERROR_INVALID_ORIENTATION,
)


class GameService:
    """Game-Service Object that handles State Management and Communication."""

    def __init__(self, size: int):
        """Implement Construcotr."""
        pass

    def get_error_messages(self):
        """Returns all possible Error-Messages."""
        return (
            ERROR_INVALID_ORIENTATION,
            ERROR_EDGE_TAKEN,
            ERROR_GAME_OVER,
            ERROR_OUT_OF_BOUNDS,
        )

    def make_move(self):
        """Implement."""
        pass

    def get_state(self):
        """Implement."""
        pass

    def restart_game(self):
        """Implement."""
        pass

    def is_game_over(self):
        """Implement."""
        pass

    def get_winner(self):
        """Implement."""
        pass
