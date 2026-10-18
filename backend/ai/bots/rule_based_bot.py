"""Rule Based Bot that performs smarter Moves than Random Bot."""

import random

import numpy as np
from backend.ai.bots.move import Move
from backend.ai.bots.basic_bot import BasicBot
from backend.game.game_board import Orientation

import logging

logger = logging.getLogger(__name__)


class RuleBasedBot(BasicBot):
    """Rule-based Bot that performs Moves with a simple logic."""

    BOT_NAME = "Rule"

    def __init__(self, size: int):
        """Rule-based Bot Constructor."""
        self.size = size
        self.positions: list[Move] = []
        self.boxes: np.ndarray = np.full((size, size), -4, dtype=int)
        self._init_positions()
        self.MAX_RANDOM_ATTEMPTS = 15

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
        self.boxes = np.full((self.size, self.size), -4, dtype=int)

    def update_game_state(self):
        """Update Game State."""

    def update(self, x: int, y: int, orientation: Orientation):
        """Update Positions and Boxes."""
        for pos in self.positions:
            if pos.x == x and pos.y == y and pos.orientation == orientation:
                pos.update()
                break
        # Boxes
        if orientation == Orientation.HORIZONTAL:
            # Box below
            if y < self.size:
                self.boxes[x, y] += 1
                if self.boxes[x, y] == 0:
                    self.boxes[x, y] = 1
            # Box above
            if y > 0:
                self.boxes[x, y - 1] += 1
                if self.boxes[x, y - 1] == 0:
                    self.boxes[x, y - 1] = 1

        # Vertical
        elif orientation == Orientation.VERTICAL:
            # Box right
            if x < self.size:
                self.boxes[x, y] += 1
                if self.boxes[x, y] == 0:
                    self.boxes[x, y] = 1
            # Box left
            if x > 0:
                self.boxes[x - 1, y] += 1
                if self.boxes[x - 1, y] == 0:
                    self.boxes[x - 1, y] = 1

    def _get_adjacent_boxes(self, move: Move) -> list[tuple[int, int]]:
        """Get Coordinates of adjacent Boxes."""
        boxes = []
        x, y = move.x, move.y

        if move.orientation == Orientation.HORIZONTAL:
            if y < self.size:
                boxes.append((x, y))
            if y > 0:
                boxes.append((x, y - 1))

        elif move.orientation == Orientation.VERTICAL:
            if x < self.size:
                boxes.append((x, y))
            if x > 0:
                boxes.append((x - 1, y))

        return boxes

    def _select_move(self):
        """Evaluate best Move."""
        possible_moves = [move for move in self.positions if move.available]

        if not possible_moves:
            logger.warning("No possible Moves available.")
            raise RuntimeError("No possible Moves available.")

        # Shuffle to generate different Moves
        random.shuffle(possible_moves)

        boxes = self.boxes

        # get win (box has 1 open Edge)
        for move in possible_moves:
            if any(boxes[x, y] == -1 for x, y in self._get_adjacent_boxes(move)):
                return move

        # produce win (create boxes with 2 open Edges)
        safe_moves = []
        for move in possible_moves:
            adj_boxes = self._get_adjacent_boxes(move)
            if all(boxes[x, y] < -2 for x, y in adj_boxes):
                safe_moves.append(move)

        if safe_moves:
            return random.choice(safe_moves)

        return random.choice(possible_moves)
