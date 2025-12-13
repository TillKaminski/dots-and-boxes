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

    BOT_NAME: str = "NOT-IMPLEMENTED"
    GAME_STATE_REQUIRED: bool = False

    @classmethod
    def name(cls) -> str:
        """Return bot name for logging or stats."""
        return cls.BOT_NAME

    @classmethod
    def game_state_required(cls) -> bool:
        """Returns if Game-State is required for predictions."""
        return cls.GAME_STATE_REQUIRED
    
    def move(
        self, log_move: bool = False, return_dictionary: bool = False
    ) -> Dict[str, Any] | Move:
        """Select a move.

        Returns dict: {"x": int, "y": int, "orientation": "horizontal|vertical"}
        """
        selected_move: Move = self._select_move()

        if log_move:
            print(f"[{self.name()}] Selected move: {selected_move}")
        
        if return_dictionary:
            return {
                "x": selected_move.x,
                "y": selected_move.y,
                "orientation": selected_move.orientation.name.lower(),
            }

        return selected_move
    
    @abstractmethod
    def _select_move(
        self, log_move: bool = False, return_dictionary: bool = False
    ) -> Dict[str, Any] | Move:
        """Select a move."""
        raise NotImplementedError("Subclass: _select_move()-Method not implemented.")

    @abstractmethod
    def reset(self) -> None:
        """Reset bot to initial state for a new game."""
        raise NotImplementedError("Subclass: reset()-Method not implemented.")

    @abstractmethod
    def update(self, x: int, y: int, orientation: Orientation) -> None:
        """Update internal state based on an applied move (self or opponent)."""
        raise NotImplementedError("Subclass: update()-Method not implemented.")


