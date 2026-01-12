"""Implementation of a Bot that uses a Feed-Forward Network to predict Moves."""

import logging
import os
import random
from typing import Any, Dict

import torch
from ai.bots.basic_bot import BasicBot
from ai.bots.move import Move
from ai.config.params import DeploymentConfig, ModelConfig
from ai.data.data_preprocessing import DataPreprocessor
from ai.model.ffn_model import FeedForwardNet
from game.game_board import Orientation
from game.game_state import GameState

logger = logging.getLogger(__name__)


class FFNBot(BasicBot):
    """Bot Class that uses a FFN for Predictions based on the current Game State."""

    BOT_NAME = "FFN"
    GAME_STATE_REQUIRED = True

    def __init__(
        self,
        size: int,
        model_path: str = DeploymentConfig.MODEL_PATH,
        epsilon: float = 0.0,
    ):
        """Constructor for a Bot that uses a FFN for Move Predictions."""
        self.size = size
        self.model_path = model_path
        self.epsilon = epsilon
        self.positions: list[Move] = []
        self.preprocessor = DataPreprocessor(size=size)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self._current_state: GameState | None = None

        self.model = self._load_model()
        self._init_positions()

    def _load_model(self) -> FeedForwardNet:
        """Load pretrained FFN-Model."""
        full_path = os.path.join(os.path.dirname(__file__), "../", self.model_path)

        if not os.path.exists(full_path):
            logger.warning(
                f"Model file not found at {full_path}. Using uninitialized model."
            )

        try:
            model = FeedForwardNet(
                input_size=ModelConfig.INPUT_SIZE,
                hidden_layers=ModelConfig.HIDDEN_LAYERS,
                output_size=ModelConfig.OUTPUT_SIZE,
                dropout_rate=ModelConfig.DROPOUT_RATE,
            ).to(self.device)
            model.load_state_dict(torch.load(full_path, map_location=self.device))
        except RuntimeError:
            logger.info("No Dropout set for Model. Use Default Dropout: 0.0.")
            model = FeedForwardNet(
                input_size=ModelConfig.INPUT_SIZE,
                hidden_layers=ModelConfig.HIDDEN_LAYERS,
                output_size=ModelConfig.OUTPUT_SIZE,
                dropout_rate=0.0,
            ).to(self.device)
            model.load_state_dict(torch.load(full_path, map_location=self.device))

        model.eval()
        return model

    def reset(self) -> None:
        """Reset bot to initial state for a new game."""
        self.positions.clear()
        self._init_positions()
        self._current_state = None

    def _select_move(self) -> Dict[str, Any] | Move:
        """Predicts the best Move based on the current Game State.

        Returns dict: {"x": int, "y": int, "orientation": "horizontal|vertical"}
        """
        if self._current_state is None:
            raise RuntimeError("No Game State set.")

        if self.epsilon > 0.0 and random.random() < self.epsilon:
            return self._get_random_legal_move()

        with torch.no_grad():
            state_vector_X = self.preprocessor._serialize_state(self._current_state)

            X = state_vector_X.unsqueeze(0).to(self.device)
            output = self.model(X).squeeze(0).cpu()

            # Filter possible Moves
            move_scores = output.numpy()
            possible_moves_mask = torch.zeros(ModelConfig.OUTPUT_SIZE, dtype=torch.bool)

            for i in range(ModelConfig.OUTPUT_SIZE):
                move_obj = self._map_index_to_move(i)
                if move_obj.available:
                    possible_moves_mask[i] = True

            masked_scores = move_scores.copy()
            # Assign small negative Number for Arg/Soft-Max
            masked_scores[~possible_moves_mask.numpy()] = -1e9

            best_move_index = masked_scores.argmax()

            move = self._map_index_to_move(best_move_index)

            return move

    def update(self, x: int, y: int, orientation: Orientation) -> None:
        """Update internal state based on an applied move (self or opponent)."""
        for pos in self.positions:
            if pos.x == x and pos.y == y and pos.orientation == orientation:
                pos.update()
                break

    def update_state(self, new_state: GameState):
        """Update the current State."""
        self._current_state = new_state

    def _init_positions(self):
        """Initialize all possible moves."""
        for x in range(self.size):
            for y in range(self.size + 1):
                self.positions.append(Move(x, y, Orientation.HORIZONTAL))

        for x in range(self.size + 1):
            for y in range(self.size):
                self.positions.append(Move(x, y, Orientation.VERTICAL))

    def _map_index_to_move(self, index: int) -> Move:
        """Maps 1D Representation to corresponding Move Object."""
        if 0 <= index < len(self.positions):
            return self.positions[index]

        raise ValueError(f"Invalid Move Index '{index}'")

    def _get_random_legal_move(self) -> Move:
        """Helper-Method for Exploration."""
        legal_moves = [move for move in self.positions if move.available]
        return random.choice(legal_moves)
