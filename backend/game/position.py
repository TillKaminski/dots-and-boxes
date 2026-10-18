"""Data-Class for Moves."""

from dataclasses import dataclass
from backend.game.game_board import Orientation


@dataclass
class Position:
    """Represents a possible move on the game board."""

    x: int
    y: int
    orientation: Orientation
    available: bool = True

    def update(self):
        """Mark this move as unavailable."""
        self.available = False
