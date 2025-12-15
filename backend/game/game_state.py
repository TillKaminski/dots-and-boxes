"""Data Class for Game State Representation."""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class GameState:
    """Defines the Structure of a Game State."""

    size: int
    current_player: int
    finished: bool
    scores: Dict[int, int]
    edges: Dict[str, List[List[int]]]
    boxes: List[List[int]]
