"""Implementation of a Random Bot. """

from dataclasses import dataclass
import random
from game.game_board import Orientation


@dataclass
class Move:
    """Represents a possible move on the game board."""

    x: int
    y: int
    orientation: Orientation
    available: bool = True

    def update(self):
        """Mark this move as unavailable."""
        self.available = False


class RandomBot:
    """A simple bot that selects random available moves."""

    def __init__(self, size: int):
        """Creates a new Random-Bot."""
        self.size = size
        self.positions: list[Move] = []
        self._init_positions()

    def _init_positions(self):
        """Initialize all possible moves for the given board."""
        for y in range(self.size + 1):
            for x in range(self.size):
                self.positions.append(Move(x, y, Orientation.HORIZONTAL))

        for y in range(self.size):
            for x in range(self.size + 1):
                self.positions.append(Move(x, y, Orientation.VERTICAL))

    def reset(self) -> None:
        """Resets the Bot for following Games."""
        self.positions.clear()
        self._init_positions()

    def move(self, log_move: bool = False, ret_dict: bool = False):
        """Select and return a random available move."""
        possible_moves = [move for move in self.positions if move.available]

        if not possible_moves:
            if log_move:
                print("No possible Moves available.")
            raise RuntimeError("No possible Moves available.")
        move = random.choice(possible_moves)

        if ret_dict:
            if log_move:
                print(
                    f"RandomBot move: x={move.x}, y={move.y}, orientation={move.orientation.name.lower()}"
                )
            return {
                "x": move.x,
                "y": move.y,
                "orientation": move.orientation.name.lower(),
            }
        if log_move:
            print(
                f"RandomBot move: x={move.x}, y={move.y}, orientation={move.orientation}"
            )
        return move

    def update_positions(self, x: int, y: int, orientation: Orientation):
        """Update Positions."""
        for pos in self.positions:
            if pos.x == x and pos.y == y and pos.orientation == orientation:
                pos.update()
                break
