"""Test-Class for API-Calls."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
game_id = "1"


def test_root_connection():
    """Test root-Function."""
    response = client.get("/")
    data = response.json()
    assert response.status_code == 200
    assert "root-message" in data
    assert "api-version" in data
    assert "status" in data


def test_game_router_connection():
    """Test if Game-Router is included."""
    response = client.get("/v1/games")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "status" in data
