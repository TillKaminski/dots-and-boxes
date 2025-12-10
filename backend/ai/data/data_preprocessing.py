"""Preprocesses raw Data for the Training of the Neural Networks."""

import argparse
import torch
import numpy as np
from typing import Any, Tuple, Dict

from ai.data.data_storage import DataStorage
from game.game_state import GameState


class DataPreprocessor:
    """Preprocesses Dots and Boxes Game Data."""

    def __init__(self, size: int):
        """Constructor for the Preprocessor based on the board size."""
        self.size = size
        self.num_boxes = size * size
        self.num_horizontal_edges = size * (size + 1)
        self.num_vertical_edges = (size + 1) * size
        self.input_size = (
            self.num_horizontal_edges + self.num_vertical_edges + self.num_boxes
        )
        self.output_size = self.num_horizontal_edges + self.num_vertical_edges

    def _serialize_state(self, state: Dict[str, Any] | GameState) -> torch.Tensor:
        """Transforms the Board State into a 1D input Vector X.

        **Order**: [Horizontal Edges, Vertical Edges, Boxes State].
        """
        if isinstance(state, GameState):
            horizontal_edges = np.array(state.edges["horizontal"]).flatten()
            vertical_edges = np.array(state.edges["vertical"]).flatten()
            boxes_raw = np.array(state.boxes).flatten()
            current_player = state.currentPlayer
        else:
            horizontal_edges = np.array(state["edges"]["horizontal"]).flatten()
            vertical_edges = np.array(state["edges"]["vertical"]).flatten()
            boxes_raw = np.array(state["boxes"]).flatten()
            current_player = state["currentPlayer"]

        horizontal_norm = self._normalize_edges(horizontal_edges)
        vertical_norm = self._normalize_edges(vertical_edges)
        boxes_norm = self._normalize_boxes(boxes_raw, current_player)

        # Combine Input
        input_vector = np.concatenate([horizontal_norm, vertical_norm, boxes_norm])

        # Check Size
        if len(input_vector) != self.input_size:
            raise ValueError(
                f"Expected input size {self.input_size}, got {len(input_vector)}"
            )

        return torch.tensor(input_vector, dtype=torch.float32)

    def _normalize_edges(self, edges_raw: np.ndarray) -> np.ndarray:
        """Normalizes all Edges, 0 -> free 1 -> occupied."""
        edges_normalized = np.zeros_like(edges_raw, dtype=np.float32)

        for i, edge_value in enumerate(edges_raw):
            if edge_value > 0:
                edges_normalized[i] = 1.0

        return edges_normalized

    def _normalize_boxes(
        self, boxes_raw: np.ndarray, current_player: int
    ) -> np.ndarray:
        """Normalizes all Boxes from the current player's perspective.

        **Normalized Values**:
        - 1.0: Box current player.
        - -1.0: Box opponent.
        - [0.0, 0.25, 0.5, 0.75]: Percentage of closure for an open box (edges drawn / 4.0).
        """
        boxes_normalized = np.zeros_like(boxes_raw, dtype=np.float32)

        for i, box_value in enumerate(boxes_raw):
            if box_value == current_player:
                boxes_normalized[i] = 1.0
            elif box_value > 0:
                boxes_normalized[i] = -1.0
            else:
                num_drawn_edges = 4 + box_value
                boxes_normalized[i] = num_drawn_edges / 4.0

        return boxes_normalized

    def _move_to_label(self, move: Dict[str, Any]) -> torch.Tensor:
        """Transforms a move into a one-hot encoded output vector Y (target move).

        The output vector Y has the size of all possible moves (Output_size).
        """
        # Map Move to One-Hot
        x, y = move["x"], move["y"]
        orientation = move["orientation"]
        one_hot_label = torch.zeros(self.output_size, dtype=torch.float32)

        if orientation == "HORIZONTAL":
            h_cols = self.size
            idx = y * h_cols + x

            one_hot_label[idx] = 1.0

        elif orientation == "VERTICAL":
            v_offset = self.num_horizontal_edges
            v_cols = self.size + 1

            idx = v_offset + y * v_cols + x

            one_hot_label[idx] = 1.0

        # Check Mapping
        if torch.sum(one_hot_label) == 0:
            raise ValueError(
                f"Move {x, y, orientation} could not be mapped to a valid index."
            )

        return one_hot_label

    def get_data_pair(
        self, step_data: Dict[str, Any]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Processes a single game step into an (Input, Target) pair."""
        # X: State Before
        X = self._serialize_state(step_data["state_before"])

        # Y: Move (One-Hot-Encoding)
        Y = self._move_to_label(step_data["move"])

        return X, Y


def main():
    """Method that handles Terminal Input."""
    parser = argparse.ArgumentParser(
        description="Prepares Training-Data for the Training Process."
    )
    parser.add_argument(
        "--ffn",
        dest="ffn",
        action="store_true",
        help="Create Dataset for the Feedforward Net.",
    )
    parser.set_defaults(ffn=False)

    parser.add_argument(
        "--pvn",
        dest="pvn",
        action="store_true",
        help="Create Dataset for the Policy-Value Net.",
    )
    parser.set_defaults(pvn=False)

    args = parser.parse_args()

    data_preprocessor = DataPreprocessor(size=4)  # TODO: Fix Magic Number
    data_storage = DataStorage()

    # Load Data
    data_raw = data_storage.load_from_pt()

    if args.ffn:
        data: list[Tuple[torch.Tensor, torch.Tensor]] = []
        for game in data_raw.values():
            for step in game:
                # Map State
                state = data_preprocessor.get_data_pair(step_data=step)
                data.append(state)

        file_path = data_storage.save_to_pt(data, filename="training_data_ffn.pt")
        print(f"Training Data for FFN saved.\n➡️ Filepath: {file_path}\n")
    elif args.pvn:
        print("TODO: Implement Preprocessing for PVN.")


if __name__ == "__main__":  # pragma: no cover
    main()
