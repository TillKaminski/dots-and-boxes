"""Class that handles save, load and print data."""

import logging
import os
import json
import torch

logger = logging.getLogger(__name__)
FILE_NAME = "training_data_raw"


class DataStorage:
    """Stores Data in Json and PT Format."""

    def __init__(self, log: bool = False):
        """Data-Storage Constructor."""
        self.file_path = ""
        self.log = log

    def save_to_json(self, data: dict, filename: str = f"{FILE_NAME}.json"):
        """Save Training Data to JSON format."""
        output_dir = os.path.join(os.path.dirname(__file__), "../outputs")
        os.makedirs(output_dir, exist_ok=True)

        file_path = os.path.join(output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        if self.log:
            logger.info(f"Saved JSON data to {file_path}")
        return file_path

    def load_from_json(self, filename: str = f"{FILE_NAME}.json"):
        """Load Training Data from JSON."""
        output_dir = os.path.join(os.path.dirname(__file__), "../outputs")
        file_path = os.path.join(output_dir, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"JSON file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if self.log:
            logger.info(f"Loaded JSON data from {file_path}")
        return data

    def save_to_pt(self, data, filename: str = f"{FILE_NAME}.pt"):
        """Save Data as PyTorch .pt (pickle)."""
        output_dir = os.path.join(os.path.dirname(__file__), "../outputs")
        os.makedirs(output_dir, exist_ok=True)

        file_path = os.path.join(output_dir, filename)
        torch.save(data, file_path)

        if self.log:
            logger.info(f"Saved PT data to {file_path}")
        return file_path

    def load_from_pt(self, filename: str = f"{FILE_NAME}.pt"):
        """Load PyTorch .pt file."""
        output_dir = os.path.join(os.path.dirname(__file__), "../outputs")
        file_path = os.path.join(output_dir, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PT file not found: {file_path}")

        data = torch.load(file_path)

        if self.log:
            logger.info(f"Loaded PT data from {file_path}")
        return data

    def print_training_data_summary(
        self, data: dict, limit_games: int = 3, limit_states: int = 10
    ):
        """Creates a Data Summary."""
        logger.info("Write Data Summary.")
        print(
            f"\n # Number of Games: {len(data)}\t-\tPrint {min(len(data), limit_games)} Games:"
        )
        for i, (game_id, states) in enumerate(data.items()):
            print(
                f"\n ## Game {game_id} – {len(states)} Turns\tfinal: {states[-1]['move']['scores']}"
            )
            len_states = min(len(states), limit_states)
            for j, (state) in enumerate(states[:len_states]):
                move = state.get("move")
                print(
                    f" # {j + 1} #\t x={move.get('x')}, y={move['y']}, \torientation={move['orientation']}\tscores: {move['scores']}"
                )
            if i + 1 >= limit_games:
                break
