"""Data Class for Game State Representation."""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class GameState:
    """Defines the Structure of a Game State."""

    size: int
    currentPlayer: int
    finished: bool
    scores: Dict[int, int]
    edges: Dict[str, List[List[int]]]
    boxes: List[List[int]]
