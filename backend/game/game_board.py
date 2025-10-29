"""Class for Game Objects and Logic."""

# from typing import Optional
import numpy as np
from enum import Enum, auto


class Orientation(Enum):
    """Enumeration to distinguish between Edge orientation."""

    HORIZONTAL = auto()
    VERTICAL = auto()


class GameBoard:
    """Representation of Game Board."""

    def __init__(self, size: int):
        """Game Board Constructor.

        Creates a new Board. Configuration is stored in 3 matrices:
        - horizontal edges: (size, size + 1)
        - vertical edges: (size + 1, size)
        - boxes: (size, size)
        Positions are from bottom left to top right (Classical Coordinate System).
        """
        self.size = size
        self.edges_horizontal: np.ndarray = np.zeros((size, size + 1), dtype=int)
        self.edges_vertical: np.ndarray = np.zeros((size + 1, size), dtype=int)
        self.boxes: np.ndarray = np.zeros((size, size), dtype=int)
        self.scores: dict[int, int] = {1: 0, 2: 0}
        self.current_player: int = 0

    def move(self, row: int, col: int, orientation: Orientation):
        """Handle Move-Action.

        Returns:
            Current Board
        """
        print(f"Board.move() called: row = {row}, col = {col} - {orientation}")
        return None
