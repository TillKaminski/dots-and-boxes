"""Test Class for Data Storage."""

import pytest

import json
import os
import torch
from ai.data.data_storage import DataStorage


@pytest.fixture
def setup_filepath(tmp_path, monkeypatch):
    """Setup Filepath for each Test."""
    fake_module_path = tmp_path / "module"
    fake_module_path.mkdir()
    fake_file = fake_module_path / "dummy.py"
    fake_file.write_text("")

    monkeypatch.setattr("ai.data.data_storage.__file__", str(fake_file))


def test_save_and_load_json(setup_filepath):  # tmp_path, monkeypatch):
    """Test if storing and loading data works."""
    data_storage = DataStorage(log=False)

    test_data = {"a": 1, "b": 2}
    file_path = data_storage.save_to_json(test_data, filename="test.json")

    assert os.path.exists(file_path)

    loaded = data_storage.load_from_json("test.json")
    assert loaded == test_data


def test_load_json_file_not_found(setup_filepath):
    """Test if an invalid Filepath throws an Exception."""
    data_storage = DataStorage()
    invalid_file_path = "does_not_exist.json"

    with pytest.raises(FileNotFoundError):
        data_storage.load_from_json(invalid_file_path)


def test_save_and_load_pt(setup_filepath):
    """Test if storing data in .pt-Format works."""
    data_storage = DataStorage()

    test_data = {"a": torch.tensor([1, 2, 3])}
    file_path = data_storage.save_to_pt(test_data, filename="data.pt")

    assert os.path.exists(file_path)

    data = data_storage.load_from_pt("data.pt")
    assert torch.equal(data["a"], test_data["a"])


def test_load_pt_file_not_found(setup_filepath):
    """Test if an invalid Filepath throws an Exception."""
    data_storage = DataStorage()
    invalid_file_path = "missing.pt"

    with pytest.raises(FileNotFoundError):
        data_storage.load_from_pt(invalid_file_path)


def test_print_training_data_summary(capsys):
    """Test if Print Function uses correct Data."""
    data_storage = DataStorage()

    test_data = {
        "game_1": [
            {"move": {"x": 1, "y": 2, "orientation": "H", "scores": {"1": 1, "2": 0}}},
            {"move": {"x": 2, "y": 3, "orientation": "V", "scores": {"1": 2, "2": 1}}},
        ],
        "game_2": [
            {"move": {"x": 1, "y": 2, "orientation": "H", "scores": {"1": 1, "2": 0}}},
            {"move": {"x": 2, "y": 3, "orientation": "V", "scores": {"1": 2, "2": 1}}},
        ],
    }

    data_storage.print_training_data_summary(test_data)

    captured = capsys.readouterr()
    assert "Number of Games: 2" in captured.out
    assert "Game game_1" in captured.out
    assert "x=1" in captured.out
    assert "y=3" in captured.out

    length_data = len(captured.out)

    # Compare Printing different number of Games
    data_storage.print_training_data_summary(test_data, limit_games=1)
    captured = capsys.readouterr()
    assert len(captured.out) != length_data
