"""Test-Class for API-Calls."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from main import main
except ImportError:
    print("Error: 'main.py' Import")
    raise


def test_main_function_runs_and_prints(capsys):
    """Test main-Method."""
    main()
    captured = capsys.readouterr()
    assert captured.out == "Python Main.\n"
    assert captured.err == ""
