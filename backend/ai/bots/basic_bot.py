"""Basic Bot Interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from ai.bots.move import Move
from game.game_board import Orientation


class BasicBot(ABC):
    """Basic Interface for all Bots.

    - reset()
    - move(log_move, return_dictionary)
    - update(x, y, orientation)
    - name()
    """

    @abstractmethod
    def reset(self) -> None:
        """Reset bot to initial state for a new game."""
        raise NotImplementedError("Subclass: reset()-Method not implemented.")

    @abstractmethod
    def move(
        self, log_move: bool = False, return_dictionary: bool = False
    ) -> Dict[str, Any] | Move:
        """Select a move.

        Returns dict: {"x": int, "y": int, "orientation": "horizontal|vertical"}
        """
        raise NotImplementedError("Subclass: move()-Method not implemented.")

    @abstractmethod
    def update(self, x: int, y: int, orientation: Orientation) -> None:
        """Update internal state based on an applied move (self or opponent)."""
        raise NotImplementedError("Subclass: update()-Method not implemented.")

    @abstractmethod
    def name(self) -> str:
        """Return bot name for logging or stats."""
        raise NotImplementedError("Subclass: name()-Method not implemented.")
