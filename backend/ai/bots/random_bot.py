"""Implementation of a Random Bot."""

import random
from ai.bots.move import Move
from ai.bots.basic_bot import BasicBot
from game.game_board import Orientation

import logging

logger = logging.getLogger(__name__)


class RandomBot(BasicBot):
    """Bot that selects random available moves."""

    BOT_NAME = "Random"

    def __init__(self, size: int):
        """Creates a new Random-Bot."""
        self.size = size
        self.positions: list[Move] = []
        self._init_positions()

    def _init_positions(self):
        """Initialize all possible moves."""
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

    def _select_move(self):
        """Select and return a random available move.

        ### Params:
        - *log_move*: Log Bot Move via Terminal.
        - *return_dictionary*: Dictionary as Move Representation, Move-Object otherwise.
        """
        possible_moves = [move for move in self.positions if move.available]

        if not possible_moves:
            raise RuntimeError("No possible Moves available.")
        move = random.choice(possible_moves)

        return move

    def update(self, x: int, y: int, orientation: Orientation):
        """Update Positions."""
        for pos in self.positions:
            if pos.x == x and pos.y == y and pos.orientation == orientation:
                pos.update()
                break
