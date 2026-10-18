"""Test Model Usage."""

import torch
import torch.nn as nn

from ai.model.ffn import FeedForwardNet


def test_model_construction():
    """Test Model Constructor and Number of Layers."""
    input_size, hidden_layers, output_size, batch_size = (32, [64, 32, 16], 1, 64)
    model = FeedForwardNet(
        input_size=input_size, hidden_layers=hidden_layers, output_size=output_size
    )

    assert isinstance(model, nn.Module)

    # Linear + ReLU + Final Linear
    # +1 final Linear Layer
    expected_layers = len(hidden_layers) * 2 + 1
    assert len(model.net) == expected_layers

    test_input = torch.randn(batch_size, input_size)
    output = model(test_input)

    assert output.shape == (batch_size, output_size)

    last_layer = model.net[-1]
    assert isinstance(last_layer, nn.Linear)
    assert last_layer.out_features == output_size
