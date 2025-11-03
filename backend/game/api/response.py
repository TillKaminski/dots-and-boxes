"""Defines Response Format."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class MetaModel(BaseModel):
    """Meta-Data Definition."""

    game_id: str = Field(..., json_schema_extra={"example": "1"})
    version: str = Field(default="v1", json_schema_extra={"example": "v1"})


class StateModel(BaseModel):
    """Service-Layer Response."""

    size: int
    edges: Dict[str, List[List[int]]]
    boxes: List[List[int]]
    scores: Dict[str, int]
    finished: bool
    currentPlayer: int


class GameResponse(BaseModel):
    """API Response."""

    meta: MetaModel
    state: StateModel


class ErrorResponse(BaseModel):
    """Error Format."""

    error: str
    code: Optional[int] = Field(default=None, json_schema_extra={"example": "message"})


class MoveRequest(BaseModel):
    """Format for Move-Actions."""

    x: int
    y: int
    orientation: str
