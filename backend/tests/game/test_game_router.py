"""Test-Class for API-Calls."""

from fastapi.testclient import TestClient
import pytest
from main import app, service
from game.errors import (
    ERROR_EDGE_TAKEN,
    ERROR_GAME_EXISTS,
    ERROR_GAME_NOT_FOUND,
    ERROR_GAME_OVER,
    ERROR_INVALID_ORIENTATION,
    ERROR_OUT_OF_BOUNDS,
)

client = TestClient(app)
game_id = "1"

URL_PREFIX = "/v1/games"


@pytest.fixture(autouse=True)
def setup_game():
    """Creates a new Game-Service Object with 2x2 Board."""
    if game_id not in service.games:
        service.create_game(game_id=game_id, size=2)
    else:
        service.restart_game(game_id=game_id)
    print(service.games)
    return service


def test_root_connection():
    """Test root-Function."""
    response = client.get(URL_PREFIX)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_new_game():
    """Test if starting a new Game returns the correct Game-ID."""
    new_id = "2"
    new_game_body = {}  # empty Request Body (starting_player and bot_model can be set)
    response = client.post(URL_PREFIX + f"/new_game/{new_id}", json=new_game_body)
    assert response.status_code == 200
    assert isinstance(service.get_state("2"), dict)

    data = response.json()
    assert data["meta"]["game_id"] == new_id


def test_get_state_initial():
    """Test if GET /state returns correct data for given Game-IDs."""
    response = client.get(URL_PREFIX + f"/{game_id}/state")
    assert response.status_code == 200

    # Matching Game-Id
    assert response.json()["meta"]["game_id"] == game_id

    data = response.json()["state"]
    assert isinstance(data, dict)
    assert "size" in data
    assert "edges" in data
    assert data["currentPlayer"] == 1
    assert data["finished"] is False
    assert data["scores"] == {"1": 0, "2": 0} or data["scores"] == {1: 0, 2: 0}


def test_json_format():
    """Test if returned JSON contains all fields."""
    response = client.get(URL_PREFIX + f"/{game_id}/state")
    data = response.json()
    required_keys = {"size", "edges", "boxes", "scores", "currentPlayer", "finished"}
    meta_keys = {"game_id", "version"}
    assert required_keys.issubset(data["state"].keys())
    assert meta_keys.issubset(data["meta"].keys())


def test_post_move_updates_state():
    """Test Game-State after POST /move."""
    response = client.post(
        URL_PREFIX + f"/{game_id}/move",
        json={"player_id": 1, "x": 0, "y": 0, "orientation": "horizontal"},
    )
    assert response.status_code == 200

    data = response.json()["state"]
    assert data["edges"]["horizontal"][0][0] == 1
    assert data["boxes"][0][0] == -3
    assert data["currentPlayer"] == 2
    assert data["finished"] is False


def test_multiple_moves():
    """Test if Board-Configuration is consistent after multiple Actions."""
    moves = [
        {"player_id": 1, "x": 0, "y": 0, "orientation": "horizontal"},
        {"player_id": 2, "x": 0, "y": 0, "orientation": "vertical"},
        {"player_id": 1, "x": 1, "y": 0, "orientation": "horizontal"},
        {"player_id": 2, "x": 0, "y": 1, "orientation": "vertical"},
    ]
    for move in moves:
        response = client.post(URL_PREFIX + f"/{game_id}/move", json=move)
        assert response.status_code == 200

    final_state = client.get(URL_PREFIX + f"/{game_id}/state").json()["state"]
    assert "boxes" in final_state
    assert (
        any(val > 0 for row in final_state["boxes"] for val in row)
        or final_state["finished"] is False
    )


def test_restart_game_resets_state():
    """Test POST /restart resets current Game."""
    client.post(
        URL_PREFIX + f"/{game_id}/move",
        json={"player_id": 1, "x": 0, "y": 0, "orientation": "horizontal"},
    )
    state_before = client.get(URL_PREFIX + f"/{game_id}/state").json()["state"]

    response = client.post(URL_PREFIX + f"/{game_id}/restart")
    assert response.status_code == 200
    new_state = response.json()["state"]

    # Check Board reset
    assert all(val == 0 for row in new_state["edges"]["horizontal"] for val in row)
    assert all(val == 0 for row in new_state["edges"]["vertical"] for val in row)
    assert new_state["currentPlayer"] == 1
    assert new_state["scores"] == {"1": 0, "2": 0} or new_state["scores"] == {
        1: 0,
        2: 0,
    }
    assert state_before != new_state


def test_move_after_restart():
    """Test if Move-Action works after restart."""
    client.post(URL_PREFIX + f"{game_id}/restart")
    response = client.post(
        URL_PREFIX + f"/{game_id}/move",
        json={"player_id": 1, "x": 0, "y": 0, "orientation": "horizontal"},
    )
    assert response.status_code == 200


def test_restart_invalid_id():
    """Test if Restarting a non-existing Game throws an Error."""
    invalid_game_id = "999"
    assert invalid_game_id not in service.games
    response = client.post(URL_PREFIX + f"/{invalid_game_id}/restart")
    assert response.status_code == 404
    assert ERROR_GAME_NOT_FOUND["error"] in response.text


def test_move_out_of_bounds():
    """Tests if input is in the correct range."""
    response = client.post(
        URL_PREFIX + f"/{game_id}/move",
        json={"player_id": 1, "x": 5, "y": 5, "orientation": "horizontal"},
    )
    assert response.status_code == 400
    assert ERROR_OUT_OF_BOUNDS["error"] in response.text


def test_move_invalid_orientation():
    """Tests Invalid Orientation."""
    response = client.post(
        URL_PREFIX + f"/{game_id}/move", json={"player_id": 1, "x": 0, "y": 0, "orientation": "invalid"}
    )
    assert response.status_code == 400
    assert ERROR_INVALID_ORIENTATION["error"] in response.text


def test_move_on_taken_edge():
    """Test Occupied Edges."""
    client.post(
        URL_PREFIX + f"/{game_id}/move",
        json={"player_id": 1, "x": 0, "y": 0, "orientation": "horizontal"},
    )
    response = client.post(
        URL_PREFIX + f"/{game_id}/move",
        json={"player_id": 2, "x": 0, "y": 0, "orientation": "horizontal"},
    )
    assert response.status_code == 409
    assert ERROR_EDGE_TAKEN["error"] in response.text


def test_invalid_game_id_returns_error():
    """Test invalid Game-ID."""
    id_invalid = "999"
    response = client.get(URL_PREFIX + f"/{id_invalid}/state")
    assert response.status_code == 404
    assert ERROR_GAME_NOT_FOUND["error"] in response.text


def test_move_after_game_finished():
    """Test if moves are rejected after Game End."""
    board = service.games[game_id]
    board.game_finished = True

    response = client.post(
        URL_PREFIX + f"/{game_id}/move",
        json={"player_id": 1, "x": 0, "y": 0, "orientation": "horizontal"},
    )
    assert response.status_code == 403
    assert ERROR_GAME_OVER["error"] in response.text


def test_multiple_games_parallel():
    """Test if two Games work independently."""
    id2 = "2"
    service.create_game(game_id=id2, size=2)

    client.post(
        URL_PREFIX + f"/{game_id}/move",
        json={"player_id": 1, "x": 0, "y": 0, "orientation": "horizontal"},
    )
    client.post(
        URL_PREFIX + f"/{id2}/move", json={"player_id": 1, "x": 1, "y": 1, "orientation": "horizontal"}
    )

    state1 = client.get(URL_PREFIX + f"/{game_id}/state").json()["state"]
    state2 = client.get(URL_PREFIX + f"/{id2}/state").json()["state"]

    assert state1 != state2
    assert state1["edges"]["horizontal"][0][0] == 1
    assert state2["edges"]["horizontal"][1][1] == 1


def test_create_new_game_existing_id():
    """Test if Creating a new Game with an existing ID returns an Error."""
    new_game_body = {}
    response = client.post(URL_PREFIX + f"/new_game/{game_id}", json=new_game_body)
    assert response.status_code == 409
    assert ERROR_GAME_EXISTS["error"] in response.text


def test_game_finished_detected():
    """Test if API Calls are correct for finished Games."""
    # Simulate Game
    board = service.games[game_id]
    board.scores = {1: 3, 2: 0}
    board.game_finished = True

    response = client.get(URL_PREFIX + f"/{game_id}/state")
    data = response.json()["state"]
    assert data["finished"] is True
