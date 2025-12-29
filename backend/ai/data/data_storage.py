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
        self.log = log

    def get_path(self, filename: str) -> str:
        """Returns the file Path."""
        output_dir = os.path.join(os.path.dirname(__file__), "../outputs", "data")
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, filename)

    def save_to_json(self, data: dict, filename: str = f"{FILE_NAME}.json"):
        """Save Training Data to JSON format."""
        file_path = self.get_path(filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        if self.log:
            logger.info(f"Saved JSON data to {file_path}")
        return file_path

    def load_from_json(self, filename: str = f"{FILE_NAME}.json"):
        """Load Training Data from JSON."""
        file_path = self.get_path(filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"JSON file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if self.log:
            logger.info(f"Loaded JSON data from {file_path}")
        return data

    def save_to_pt(self, data, filename: str = f"{FILE_NAME}.pt"):
        """Save Data as PyTorch .pt (pickle)."""
        file_path = self.get_path(filename)
        torch.save(data, file_path)

        if self.log:
            logger.info(f"Saved PT data to {file_path}")
        return file_path

    def load_from_pt(self, filename: str = f"{FILE_NAME}.pt"):
        """Load PyTorch .pt file."""
        file_path = self.get_path(filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PT file not found: {file_path}")

        data = torch.load(file_path)

        if self.log:
            logger.info(f"Loaded PT data from {file_path}")
        return data

    def merge_and_save(self, new_data: dict, filename: str, prefix: str = "game"):
        """Loads old Data and appends new Data."""
        path = self.get_path(filename)

        if os.path.exists(path):
            existing_data = torch.load(path)
            logger.info(
                f"Merging {len(new_data)} new games into {len(existing_data)} existing games."
            )
        else:
            existing_data = {}
            logger.info(f"No existing file found. Creating {filename}.")

        current_count = len(existing_data)
        for i, (_, states) in enumerate(new_data.items()):
            new_id = f"{prefix}_{current_count + i + 1}"
            existing_data[new_id] = states

        torch.save(existing_data, path)
        print(f"Successfully saved. Total games in {filename}: {len(existing_data)}")
        logger.info(
            f"Successfully saved. Total games in {filename}: {len(existing_data)}"
        )

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
