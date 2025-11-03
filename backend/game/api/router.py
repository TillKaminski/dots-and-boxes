"""Routes for Game-APIs."""

from fastapi import APIRouter, HTTPException, Depends
from game.errors import ERROR_INVALID_ORIENTATION, get_error_response
from game.game_board import Orientation
from game.game_service import GameService
from .response import GameResponse, MoveRequest

router = APIRouter(prefix="/v1/games", tags=["Games"])
# service = GameService()


def get_game_service():
    """Service-Instance."""
    from main import service

    return service


@router.get("/")
@router.get("")
def get_game_service_info():
    """Returns Information about Game-API-Service."""
    return {
        "service": "Game API",
        "status": "online",
        "api_version": "v1",
        "message": "Game operations are available at other endpoints.",
    }


@router.post("/new_game/{game_id}", response_model=GameResponse)
def new_game(game_id: str, service: GameService = Depends(get_game_service)):
    """Create a new Game for given Game-ID."""
    result = service.create_game(game_id=game_id)
    if "error" in result and result["error"]:
        error_obj, status_code = get_error_response(result["error"])
        raise HTTPException(status_code=status_code, detail=error_obj["error"])

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
    """Get Game-State for given Game-ID."""
    result = service.get_state(game_id=game_id)
    if "error" in result and result["error"]:
        error_obj, status_code = get_error_response(result["error"])
        raise HTTPException(status_code=status_code, detail=error_obj["error"])
    result["scores"] = {str(k): v for k, v in result["scores"].items()}
    response = {
        "meta": {
            "game_id": game_id,
            "version": "v1",
        },
        "state": result,
    }
    return response


@router.post("/{game_id}/move")
def move(
    game_id: str, move: MoveRequest, service: GameService = Depends(get_game_service)
):
    """Handle Player-Action Move."""
    try:
        orientation_enum = map_orientation(move.orientation)
        result = service.make_move(
            game_id=game_id,
            x=move.x,
            y=move.y,
            orientation=orientation_enum,
        )
    except ValueError as e:
        # Exception thrown
        error_obj, status_code = get_error_response(str(e))
        raise HTTPException(status_code=status_code, detail=error_obj["error"])

    # Error Message received
    if "error" in result and result["error"]:
        error_obj, status_code = get_error_response(result["error"])
        raise HTTPException(status_code=status_code, detail=error_obj["error"])

    result["scores"] = {str(k): v for k, v in result["scores"].items()}
    response = {
        "meta": {
            "game_id": game_id,
            "version": "v1",
        },
        "state": result,
    }
    return response


@router.post("/{game_id}/restart", response_model=GameResponse)
def restart_game(game_id: str, service: GameService = Depends(get_game_service)):
    """Restart Game with given Game-ID."""
    result = service.restart_game(game_id=game_id)
    if "error" in result and result["error"]:
        error_obj, status_code = get_error_response(result["error"])
        raise HTTPException(status_code=status_code, detail=error_obj["error"])

    result["scores"] = {str(k): v for k, v in result["scores"].items()}
    response = {
        "meta": {
            "game_id": game_id,
            "version": "v1",
        },
        "state": result,
    }
    return response


def map_orientation(value: str) -> Orientation:
    """Map string from request to Orientation Enum."""
    mapping = {
        "horizontal": Orientation.HORIZONTAL,
        "vertical": Orientation.VERTICAL,
    }
    try:
        return mapping[value.lower()]
    except KeyError:
        raise ValueError(ERROR_INVALID_ORIENTATION["error"])
