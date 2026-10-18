"""Defines Response Format."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional

from backend.game.game_board import Orientation


def to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class CamelCaseBaseModel(BaseModel):
    """Base model with configuration for automatic camelCase conversion.

    All other API models should inherit from this class.
    """

    class Config:
        """Pydantic configuration for camelCase serialization."""

        alias_generator = to_camel_case
        populate_by_name = True
        by_alias = True


class MetaModel(CamelCaseBaseModel):
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


class StateModel(CamelCaseBaseModel):
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
    current_player: int = Field(..., description="ID of the player whose turn it is.")


class NewGameRequest(CamelCaseBaseModel):
    """Input format for creating a new game, including board size and optional bot data."""

    starting_player: Optional[int] = Field(
        default=1, description="Choose the starting player.", examples=[1, 2]
    )

    board_size: Optional[int] = Field(
        default=4, description="Choose board size.", examples=[3, 4, 5]
    )

    bot_model: Optional[str] = Field(
        default=None,
        description="Optional model name of the bot to be registered for this game.",
        examples=["random", "ffn-bot"],
    )


class RestartGameRequest(CamelCaseBaseModel):
    """Input format for restarting a game, including starting player and board size."""

    starting_player: Optional[int] = Field(
        default=1, description="Choose the starting player.", examples=[1, 2]
    )

    board_size: Optional[int] = Field(
        default=0,
        description="Choose board size. Uses old board size if empty.",
        examples=[3, 4, 5],
    )


class MoveRequest(CamelCaseBaseModel):
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


class BotMoveOutput(CamelCaseBaseModel):
    """Output format for a bot move action, without player_id."""

    x: int = Field(..., description="X coordinate of the edge.", examples=[0])
    y: int = Field(..., description="Y coordinate of the edge.", examples=[1])
    orientation: Orientation = Field(
        ...,
        description="Orientation of the edge: 'horizontal' or 'vertical'.",
        examples=["horizontal"],
    )


class GameResponse(CamelCaseBaseModel):
    """Standard API Response Format."""

    meta: MetaModel = Field(..., description="Meta information about the request.")
    state: StateModel = Field(..., description="Current game state.")

    move: Optional[BotMoveOutput] = Field(
        default=None,
        description="The executed move details, present only for /bot_move.",
    )


class ErrorResponse(CamelCaseBaseModel):
    """Error Response Format."""

    error: str = Field(..., description="Error message explaining what went wrong.")
    code: Optional[int] = Field(
        default=None,
        description="HTTP status code corresponding to the error.",
        examples=[400, 404, 409],
    )


class ServiceInfoResponse(CamelCaseBaseModel):
    """Format for Health-Checks."""

    service: str
    status: str
    api_version: str
    message: str
