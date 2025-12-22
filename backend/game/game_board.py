"""Class for Game Objects and Logic."""

import numpy as np
from enum import Enum, auto

from game.game_state import GameState
from .errors import (
    ERROR_EDGE_TAKEN,
    ERROR_OUT_OF_BOUNDS,
    ERROR_INVALID_ORIENTATION,
    ERROR_INVALID_ORIENTATION_TYPE,
)


class Orientation(str, Enum):
    """Enumeration to distinguish between Edge orientation."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class GameBoard:
    """Representation of Game Board."""

    def __init__(self, size: int, starting_player: int = 1, bot_model: str = "random"):
        """Game Board Constructor.

        Creates a new Board. Configuration is stored in 3 matrices:
        - horizontal edges: (size, size + 1)
        - vertical edges: (size + 1, size)
        - boxes: (size, size) stores open edges (neg.) or player (pos.)
        Positions are from bottom left to top right (Classical Coordinate System).
        """
        self.size = size
        self.game_finished: bool = False
        self.edges_horizontal: np.ndarray = np.zeros((size, size + 1), dtype=int)
        self.edges_vertical: np.ndarray = np.zeros((size + 1, size), dtype=int)
        self.boxes: np.ndarray = np.full((size, size), -4, dtype=int)
        self.scores: dict[int, int] = {1: 0, 2: 0}
        self.current_player: int = starting_player
        self.bot_model: str = bot_model
        self.bot_id: int = 2

    def move(self, x: int, y: int, orientation: Orientation):
        """Handle Move-Action.

        Returns:
            Current Board
        """
        self._validate_input(x, y, orientation)
        self._set_board_position(x, y, orientation)

        # Check if Box was closed
        if self._update_boxes(x, y, orientation):
            # Switch Player
            self._switch_player()

        if self.is_game_over():
            self.game_finished = True
            return

    def is_game_over(self):
        """Checks for Winning Player or Draw."""
        # Player has majority of Boxes
        score_threshold = self.size * self.size / 2
        if self.scores[1] > score_threshold or self.scores[2] > score_threshold:
            return True

        # No Boxes with open Edges: Draw
        if np.all(self.boxes > 0):
            return True

        return False

    def get_winner(self) -> int | str | None:
        """Return 1 or 2 for Winner, 'Draw' for Draw, None if game not finished."""
        if not self.is_game_over():
            return None
        score_p1, score_p2 = self.scores[1], self.scores[2]
        if score_p1 > score_p2:
            return 1
        elif score_p2 > score_p1:
            return 2
        else:
            return "Draw"

    def get_state_object(self) -> GameState:
        """Create GameState-Object."""
        return GameState(
            size=self.size,
            current_player=self.current_player,
            finished=self.game_finished,
            scores=self.scores.copy(),
            edges={
                "horizontal": self.edges_horizontal.tolist(),
                "vertical": self.edges_vertical.tolist(),
            },
            boxes=self.boxes.tolist(),
        )

    def to_json(self) -> dict:
        """Map Game Configuration to JSON."""
        return self.get_state_object().__dict__

    def _validate_input(self, x: int, y: int, orientation: Orientation):
        """Validate input parameters."""
        # Check Orientation
        orientation = parse_orientation(orientation)

        # Check if Position is in valid range
        if x < 0 or y < 0:
            raise ValueError(ERROR_OUT_OF_BOUNDS["error"])

        if orientation == Orientation.HORIZONTAL:
            if x > self.size - 1 or y > self.size:
                raise ValueError(ERROR_OUT_OF_BOUNDS["error"])

        if orientation == Orientation.VERTICAL:
            if x > self.size or y > self.size - 1:
                raise ValueError(ERROR_OUT_OF_BOUNDS["error"])

        # Check if Position is occupied
        if orientation == Orientation.HORIZONTAL:
            if self.edges_horizontal[x, y] != 0:
                raise ValueError(ERROR_EDGE_TAKEN["error"])
        else:
            if self.edges_vertical[x, y] != 0:
                raise ValueError(ERROR_EDGE_TAKEN["error"])

    def _set_board_position(self, x: int, y: int, orientation: Orientation):
        """Update Board."""
        if orientation == Orientation.HORIZONTAL:
            self.edges_horizontal[x, y] = self.current_player
        else:
            self.edges_vertical[x, y] = self.current_player

    def _update_boxes(self, x: int, y: int, orientation: Orientation):
        """Updates neighboring boxes and evaluates if one was closed."""
        switch_player = True
        # Horizontal
        if orientation == Orientation.HORIZONTAL:
            # Box below
            if y < self.size:
                self.boxes[x, y] += 1
                if self.boxes[x, y] == 0:
                    self.boxes[x, y] = self.current_player
                    self.scores[self.current_player] += 1
                    switch_player = False
            # Box above
            if y > 0:
                self.boxes[x, y - 1] += 1
                if self.boxes[x, y - 1] == 0:
                    self.boxes[x, y - 1] = self.current_player
                    self.scores[self.current_player] += 1
                    switch_player = False

        # Vertical
        elif orientation == Orientation.VERTICAL:
            # Box right
            if x < self.size:
                self.boxes[x, y] += 1
                if self.boxes[x, y] == 0:
                    self.boxes[x, y] = self.current_player
                    self.scores[self.current_player] += 1
                    switch_player = False
            # Box left
            if x > 0:
                self.boxes[x - 1, y] += 1
                if self.boxes[x - 1, y] == 0:
                    self.boxes[x - 1, y] = self.current_player
                    self.scores[self.current_player] += 1
                    switch_player = False
        return switch_player

    def _switch_player(self):
        """Switch Current Player."""
        self.current_player = 1 if (self.current_player == 2) else 2

    def print_board(self):
        """Prints the current board configuration to the Terminal."""
        print("=======" * (self.size + 1))
        print("\n")

        for y in range(self.size):
            # Print Horizontal Lines
            line = ""
            for x in range(self.size):
                line += "#"
                if y < self.size:
                    player = self.edges_horizontal[x, y]
                    edge_char = f"---{player}---" if player != 0 else "--- ---"
                    line += edge_char
            line += "#"
            print(line)

            # Print Vertical Line
            line = ""
            for x in range(self.size):
                player_v = self.edges_vertical[x, y]
                v_char = f"|{player_v}" if player_v != 0 else "| "
                line += v_char

                box_val = self.boxes[x, y]
                box_char = f"[{box_val}]" if box_val > 0 else f" {-box_val} "
                line += f" {box_char}  "

            # Print last Vertical Edge
            player_v = self.edges_vertical[self.size, y]
            v_char = f"|{player_v}" if player_v != 0 else "| "
            line += v_char
            print(line)

        # Print last Horizontal Edge
        line = ""
        for x in range(self.size):
            line += "#"
            if x < self.size:
                player = self.edges_horizontal[x, self.size]
                edge_char = f"---{player}---" if player != 0 else "--- ---"
                line += edge_char
        line += "#"
        print(line)
        print("\n")
        print("=======" * (self.size + 1))


def parse_orientation(orientation: Orientation | str | None):
    """Map String to Enum."""
    if orientation is None:
        raise TypeError(ERROR_INVALID_ORIENTATION_TYPE["error"])
    if isinstance(orientation, Orientation):
        return orientation
    if isinstance(orientation, str):
        if orientation.lower() in ["horizontal", "vertical"]:
            return Orientation[orientation.upper()]
        raise ValueError(ERROR_INVALID_ORIENTATION["error"])
    raise TypeError(ERROR_INVALID_ORIENTATION_TYPE["error"])
