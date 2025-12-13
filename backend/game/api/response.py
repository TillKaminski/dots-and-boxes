"""Defines Response Format."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class MetaModel(BaseModel):
    """Meta-Data Definition for API Responses."""

    game_id: str = Field(
        ...,
        description="Unique identifier of the game session.",
        examples=["1", "game_abc123"],
    )
    version: str = Field(
        default="v1",
        description="API version used for this response.",
        examples=["v1"],
    )


class StateModel(BaseModel):
    """Game state returned by the Service Layer."""

    size: int = Field(..., description="Size of the game board.")
    edges: Dict[str, List[List[int]]] = Field(
        ...,
        description=(
            "Dictionary with 'horizontal' and 'vertical' edge states. "
            "Each entry is a 2D array where 0 means free and 1 means taken."
        ),
        examples=[{"horizontal": [[0, 1], [0, 0]], "vertical": [[1, 0], [0, 1]]}],
    )
    boxes: List[List[int]] = Field(
        ...,
        description="Matrix representing completed boxes. 0 = empty, 1/2 = claimed by player, -3 = open.",
        examples=[[[0, 1], [0, 0]]],
    )
    scores: Dict[str, int] = Field(
        ...,
        description="Score of each player, where keys are player IDs as strings.",
        examples=[{"1": 2, "2": 1}],
    )
    finished: bool = Field(..., description="Whether the game is finished.")
    currentPlayer: int = Field(..., description="ID of the player whose turn it is.")


class NewGameRequest(BaseModel):
    """Input format for creating a new game, including optional bot data."""

    starting_player: Optional[int] = Field(
        default=1, description="Choose the starting player.", examples=[1, 2]
    )

    bot_model: Optional[str] = Field(
        default=None,
        description="Optional model name of the bot to be registered for this game.",
        examples=["random", "ffn-bot"],
    )


class GameResponse(BaseModel):
    """Standard API Response Format."""

    meta: MetaModel = Field(..., description="Meta information about the request.")
    state: StateModel = Field(..., description="Current game state.")


class ErrorResponse(BaseModel):
    """Error Response Format."""

    error: str = Field(..., description="Error message explaining what went wrong.")
    code: Optional[int] = Field(
        default=None,
        description="HTTP status code corresponding to the error.",
        examples=[400, 404, 409],
    )


class MoveRequest(BaseModel):
    """Input format for a player move action."""

    player_id: int = Field(
        ..., description="ID of the player making the move (1 or 2).", examples=[1]
    )

    x: int = Field(..., description="X coordinate of the edge.", examples=[0])
    y: int = Field(..., description="Y coordinate of the edge.", examples=[1])
    orientation: str = Field(
        ...,
        description="Orientation of the edge: 'horizontal' or 'vertical'.",
        examples=["horizontal"],
    )


class ServiceInfoResponse(BaseModel):
    """Format for Health-Checks."""

    service: str
    status: str
    api_version: str
    message: str
