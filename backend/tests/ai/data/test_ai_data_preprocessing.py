import unittest
import torch
import numpy as np
from typing import Dict, Any

from ai.data.data_preprocessing import DataPreprocessor, main

from unittest.mock import patch
import sys


class TestDataPreprocessor(unittest.TestCase):
    """Tests for the DataPreprocessor class."""

    def setUp(self):
        """Setup for all tests: Initialize preprocessor with size=2."""
        self.size = 2
        self.preprocessor = DataPreprocessor(size=self.size)

    def test_initial_size(self):
        """Test the calculation of input/output dimensions for size=2."""
        # Horizontal Edges: 2 * (2 + 1) = 6
        self.assertEqual(self.preprocessor.num_horizontal_edges, 6)
        # Vertical Edges: (2 + 1) * 2 = 6
        self.assertEqual(self.preprocessor.num_vertical_edges, 6)
        # Boxes: 2 * 2 = 4
        self.assertEqual(self.preprocessor.num_boxes, 4)
        # Input Size: 6 + 6 + 4 = 16
        self.assertEqual(self.preprocessor.input_size, 16)
        # Output Size: 6 + 6 = 12
        self.assertEqual(self.preprocessor.output_size, 12)

    def test_box_normalization_player_1(self):
        """Test normalization for Player 1."""
        current_player = 1
        # Simulate Box Configuration
        boxes_raw = np.array([1, 2, -1, -4], dtype=np.int32)

        # P1 owns (1.0), P2 owns (-1.0),
        # 3 edges drawn (4-1)/4 = 0.75
        # 0 edges drawn (4-4)/4 = 0.0
        expected_norm = np.array([1.0, -1.0, 0.75, 0.0], dtype=np.float32)

        normalized = self.preprocessor._normalize_boxes(boxes_raw, current_player)
        np.testing.assert_array_almost_equal(normalized, expected_norm)

    def test_box_normalization_player_2(self):
        """Tes normalization for Player 2."""
        current_player = 2
        # Simulate Box Configuration
        boxes_raw = np.array([1, 2, -3, -2], dtype=np.int32)

        # P1 owns (-1.0), P2 owns (1.0)
        # 1 edge drawn (4-3)/4 = 0.25
        # 2 edges drawn (4-2)/4 = 0.5
        expected_norm = np.array([-1.0, 1.0, 0.25, 0.5], dtype=np.float32)

        normalized = self.preprocessor._normalize_boxes(boxes_raw, current_player)
        np.testing.assert_array_almost_equal(normalized, expected_norm)

    def test_move_horizontal_start(self):
        """Test a horizontal move at position (0, 0) -> Index 0."""
        move = {"x": 0, "y": 0, "orientation": "HORIZONTAL"}
        # Expected: [1, 0, 0, 0, 0, 0 | 0, 0, 0, 0, 0, 0] -> (Index 0)
        expected_label = torch.zeros(12, dtype=torch.float32)
        expected_label[0] = 1.0

        label = self.preprocessor._move_to_label(move)
        self.assertTrue(torch.equal(label, expected_label))

    def test_move_horizontal_end(self):
        """Test a horizontal move at position (1, 2) -> Index 5 (Last Horizontal)."""
        move = {"x": 1, "y": 2, "orientation": "HORIZONTAL"}
        # Horizontal Edges: h_cols = size = 2. Indices: 0-1 (y=0), 2-3 (y=1), 4-5 (y=2)
        # Index = 2 * 2 + 1 = 5 (last hor. Edge)
        expected_label = torch.zeros(12, dtype=torch.float32)
        expected_label[5] = 1.0

        label = self.preprocessor._move_to_label(move)
        self.assertTrue(torch.equal(label, expected_label))

    def test_move_vertical_start(self):
        """Test a vertical move at position (0, 0) -> Index 6 (First Vertical)."""
        move = {"x": 0, "y": 0, "orientation": "VERTICAL"}
        # Vertical Offset: num_horizontal_edges = 6. Index = 6 + 0 = 6.
        expected_label = torch.zeros(12, dtype=torch.float32)
        expected_label[6] = 1.0

        label = self.preprocessor._move_to_label(move)
        self.assertTrue(torch.equal(label, expected_label))

    def test_move_vertical_end(self):
        """Test a vertical move at position (2, 1) -> Index 11 (Last Vertical)."""
        move = {"x": 2, "y": 1, "orientation": "VERTICAL"}
        # Vertical Mapping: v_cols = self.size + 1
        # index = v_offset + y * v_cols + x

        expected_label = torch.zeros(12, dtype=torch.float32)
        expected_label[11] = 1.0

        label = self.preprocessor._move_to_label(move)
        self.assertTrue(torch.equal(label, expected_label))

    def test_data_pair(self):
        """Test processing of a single Game State (State X and Move Y)."""

        # Mock Game State for a 2x2 board (size=2)
        mock_step_data: Dict[str, Any] = {
            "move": {
                "x": 0,
                "y": 1,
                "orientation": "HORIZONTAL",
                "player": 1,
                "bot_type": "random",
                "scores": {"1": 0, "2": 0},
            },
            "state_before": {
                "size": 2,
                "currentPlayer": 1,
                "finished": False,
                "scores": {"1": 0, "2": 0},
                "edges": {
                    "horizontal": [[1, 0], [0, 0], [0, 0]],
                    "vertical": [[0, 0], [1, 0], [0, 0]],
                },
                "boxes": [[1, -2], [-4, 2]],
            },
        }

        # Expected X
        # Horizontal Edges (Size 6): [1, 0, 0, 0, 0, 0]
        horizontal = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        # Vertical Edges (Size 6): [0, 0, 1, 0, 0, 0]
        vertical = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
        # Boxes: 1.0 (P1) 0.5 (2 edges drawn) 0.0 (0 edges drawn) -1.0 (P2, opponent)
        boxes = np.array([1.0, 0.5, 0.0, -1.0])

        expected_X = np.concatenate([horizontal, vertical, boxes], dtype=np.float32)

        # Move: (x=0, y=1, HORIZONTAL) -> Index 2
        expected_Y = torch.zeros(12, dtype=torch.float32)
        expected_Y[2] = 1.0

        X, Y = self.preprocessor.get_data_pair(mock_step_data)

        np.testing.assert_array_almost_equal(X.numpy(), expected_X, decimal=4)
        self.assertTrue(torch.equal(Y, expected_Y))

    @patch("ai.data.data_preprocessing.DataStorage")
    @patch("ai.data.data_preprocessing.DataPreprocessor")
    def test_main_creates_ffn_set(self, preprocessor_mock, storage_mock):
        """Test if Preprocessing is available via Terminal Call."""
        preprocessor_object = preprocessor_mock.return_value
        preprocessor_object.get_data_pair.return_value = {"X": "Feature", "Y": "Label"}

        storage_object = storage_mock.return_value
        storage_object.load_from_pt.return_value = {
            "step_1": "data_1",
            "step_2": "data_2",
        }

        test_args = ["prog", "--ffn"]
        with patch.object(sys, "argv", test_args):
            main()

        storage_object.load_from_pt.assert_called_once()
        preprocessor_object.get_data_pair.assert_called()
