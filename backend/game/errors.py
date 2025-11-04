"""File that stores all Error-Messages."""

from fastapi import status

ERROR_EDGE_TAKEN = {"error": "Edge is already taken."}
ERROR_OUT_OF_BOUNDS = {"error": "Incorrect Edge Index."}
ERROR_GAME_OVER = {"error": "Game-Session already closed."}
ERROR_INVALID_ORIENTATION = {"error": "Invalid orientation."}
ERROR_GAME_EXISTS = {"error": "Game already exists."}
ERROR_GAME_NOT_FOUND = {"error": "Game not found."}

ERROR_CODE_MAP = {
    ERROR_EDGE_TAKEN["error"]: status.HTTP_409_CONFLICT,
    ERROR_OUT_OF_BOUNDS["error"]: status.HTTP_400_BAD_REQUEST,
    ERROR_GAME_OVER["error"]: status.HTTP_403_FORBIDDEN,
    ERROR_GAME_NOT_FOUND["error"]: status.HTTP_404_NOT_FOUND,
    ERROR_GAME_EXISTS["error"]: status.HTTP_409_CONFLICT,
    ERROR_INVALID_ORIENTATION["error"]: status.HTTP_400_BAD_REQUEST,
}


def get_error_response(message: str):
    """Returns Tuple(dict, code)."""
    code = ERROR_CODE_MAP.get(message, status.HTTP_400_BAD_REQUEST)
    return {"error": message}, code
