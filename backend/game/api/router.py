"""Routes for Game-APIs."""

from fastapi import APIRouter, HTTPException, Depends
from backend.game.errors import ERROR_INVALID_ORIENTATION, get_error_response
from backend.game.game_board import Orientation
from backend.game.game_service import GameService
from .response import (
    GameResponse,
    MoveRequest,
    RestartGameRequest,
    ServiceInfoResponse,
    NewGameRequest,
)

router = APIRouter(prefix="/v1/games", tags=["Games"])


def get_game_service():
    """Service-Instance."""
    from backend.main import service

    return service


@router.get("/")
def get_game_service_info():
    """Returns Information about Game-API-Service."""
    return ServiceInfoResponse(
        service="Game API",
        status="online",
        api_version="v1",
        message="Game operations are available at other endpoints.",
    )


@router.post("/new_game/{game_id}", response_model=GameResponse)
def new_game(
    game_id: str,
    request_data: NewGameRequest,
    service: GameService = Depends(get_game_service),
):
    """Create a new Game for given Game-ID.

    ### Args
    - **game_id** *(str)* ID of the game

    ### Returns
    - **GameResponse** The initialized game state with meta information.

    ### Raises
    - **HTTPException** If the game already exists (409).
    """
    starting_player = request_data.starting_player
    board_size = request_data.board_size
    bot_name = request_data.bot_model
    result = service.create_game(
        game_id=game_id, starting_player=starting_player, size=board_size, bot_model=bot_name
    )
    _check_error_message(result)

    result["scores"] = {str(k): v for k, v in result["scores"].items()}
    response = {
        "meta": {
            "game_id": game_id,
            "version": "v1",
        },
        "state": result,
    }
    return response


@router.get("/{game_id}/state", response_model=GameResponse)
def get_state(game_id: str, service: GameService = Depends(get_game_service)):
    """Get Game-State for given Game-ID.

    ### Args
    - **game_id** *(str)* ID of the game

    ### Returns
    - **GameResponse** The initialized game state with meta information.

    ### Raises
    - **HTTPException** If the game doesn't exist (404).
    """
    result = service.get_state(game_id=game_id)
    _check_error_message(result)
    result["scores"] = {str(k): v for k, v in result["scores"].items()}
    response = {
        "meta": {
            "game_id": game_id,
            "version": "v1",
        },
        "state": result,
    }
    return response


@router.post("/{game_id}/move", response_model=GameResponse)
def move(
    game_id: str, move: MoveRequest, service: GameService = Depends(get_game_service)
):
    """Handle Player-Action Move.

    ### Args
    - **game_id** *(str)* ID of the game
        move (MoveRequest): JSON body containing x, y, and orientation

    ### Returns
    - **GameResponse** The resulting game state with meta information.

    ### Raises
    - **HTTPException** If the game is finished (403), Invalid Input (400), Edge already taken (409).
    """
    try:
        orientation_enum = _map_orientation(move.orientation)
        result = service.make_move(
            game_id=game_id,
            player_id=move.player_id,
            x=move.x,
            y=move.y,
            orientation=orientation_enum,
        )
    except ValueError as e:
        # Exception thrown
        error_obj, status_code = get_error_response(str(e))
        raise HTTPException(status_code=status_code, detail=error_obj["error"])

    # Error Message received
    _check_error_message(result)

    result["scores"] = {str(k): v for k, v in result["scores"].items()}
    response = {
        "meta": {
            "game_id": game_id,
            "version": "v1",
        },
        "state": result,
    }
    return response


@router.get("/{game_id}/bot_move", response_model=GameResponse)
def bot_move(game_id: str, service: GameService = Depends(get_game_service)):
    """Get an Action performed by the chosen Bot.

    ### Args
    - **game_id** *(str)* ID of the game

    ### Returns
    - **GameResponse** The resulting game state with meta information.

    ### Raises
    - **HTTPException** If the game is finished (403), Invalid Input (400), Edge already taken (409), Game Id not found (404).
    """
    try:
        # Returns chosen Move
        result_move = service.make_bot_move(game_id)

        # Error Message received
        _check_error_message(result_move)

        result_state = service.get_state(game_id)
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        # Exception thrown
        error_obj, status_code = get_error_response(str(e))
        raise HTTPException(status_code=status_code, detail=error_obj["error"])

    result_state["scores"] = {str(k): v for k, v in result_state["scores"].items()}
    response = {
        "meta": {
            "game_id": game_id,
            "version": "v1",
        },
        "move": result_move,
        "state": result_state,
    }
    return response


@router.post("/{game_id}/restart", response_model=GameResponse)
def restart_game(
    game_id: str,
    request_data: RestartGameRequest | None,
    service: GameService = Depends(get_game_service),
):
    """Restart Game with given Game-ID.

    ### Args
    - **game_id** *(str)*: Unique identifier of the game to restart.

    ### Returns
    - **GameResponse**: The new game state including meta information.

    ### Raises
    - **HTTPException (404)**: If the game does not exist.
    """
    # default set in Request Body
    starting_player = request_data.starting_player
    board_size = request_data.board_size
    result = service.restart_game(game_id=game_id, starting_player=starting_player, board_size=board_size)
    _check_error_message(result)

    result["scores"] = {str(k): v for k, v in result["scores"].items()}
    response = {
        "meta": {
            "game_id": game_id,
            "version": "v1",
        },
        "state": result,
    }
    return response


def _check_error_message(result):
    """Raises an HTTPException if the service returned an error."""
    error_val = None
    if isinstance(result, dict):
        error_val = result.get("error")
    else:
        error_val = getattr(result, "error", None)

    if error_val:
        error_obj, status_code = get_error_response(error_val)
        raise HTTPException(status_code=status_code, detail=error_obj["error"])


def _map_orientation(value: str) -> Orientation:
    """Map string from request to Orientation Enum."""
    mapping = {
        "horizontal": Orientation.HORIZONTAL,
        "vertical": Orientation.VERTICAL,
    }
    try:
        return mapping[value.lower()]
    except KeyError:
        raise ValueError(ERROR_INVALID_ORIENTATION["error"])
