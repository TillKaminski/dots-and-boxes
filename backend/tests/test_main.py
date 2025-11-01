"""Test-Class for API-Calls."""

from fastapi.testclient import TestClient
from main import app, main

client = TestClient(app)

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_main_output(capsys):
    """Test main-Method."""
    main()
    captured = capsys.readouterr()
    assert captured.out == "Python Main.\n"
    assert captured.err == ""


def test_root_connection():
    """Test root-Function."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"test-message": "Fast-API Test."}
