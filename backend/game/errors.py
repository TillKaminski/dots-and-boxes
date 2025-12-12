"""File that stores all Error-Messages."""

from fastapi import status

ERROR_EDGE_TAKEN = {"error": "Edge is already taken."}
ERROR_OUT_OF_BOUNDS = {"error": "Incorrect Edge Index."}
ERROR_GAME_OVER = {"error": "Game-Session already closed."}
ERROR_NOT_YOUR_TURN = {"error": "Received Player is not the current Player."}
ERROR_INVALID_ORIENTATION = {"error": "Invalid orientation."}
ERROR_INVALID_ORIENTATION_TYPE = {"error": "Invalid orientation type."}
ERROR_GAME_EXISTS = {"error": "Game already exists."}
ERROR_GAME_NOT_FOUND = {"error": "Game not found."}
ERROR_BOT_NOT_SET = {"error": "No Bot set in Game Configuration."}

ERROR_CODE_MAP = {
    ERROR_EDGE_TAKEN["error"]: status.HTTP_409_CONFLICT,
    ERROR_OUT_OF_BOUNDS["error"]: status.HTTP_400_BAD_REQUEST,
    ERROR_GAME_OVER["error"]: status.HTTP_403_FORBIDDEN,
    ERROR_NOT_YOUR_TURN["error"]: status.HTTP_409_CONFLICT,
    ERROR_GAME_NOT_FOUND["error"]: status.HTTP_404_NOT_FOUND,
    ERROR_GAME_EXISTS["error"]: status.HTTP_409_CONFLICT,
    ERROR_INVALID_ORIENTATION["error"]: status.HTTP_400_BAD_REQUEST,
    ERROR_BOT_NOT_SET["error"]: status.HTTP_409_CONFLICT
}


def get_error_response(message: str):
    """Returns Tuple(dict, code)."""
    code = ERROR_CODE_MAP.get(message, status.HTTP_400_BAD_REQUEST)
    return {"error": message}, code
