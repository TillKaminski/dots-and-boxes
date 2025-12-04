"""Defines the Model Structure."""

import torch.nn as nn


class ModelNet(nn.Module):
    """Definition of the Feed Forward Neural Network."""

    def __init__(self, input_size: int, hidden_layers: list[int], output_size: int):
        """Model Constructor.

        ### Args:
        - **input_size**
        - **hidden_layer**
        - **output_size**
        """
        super().__init__()
        layers = []
        prev_size = input_size
        for hidden_size in hidden_layers:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            prev_size = hidden_size
        layers.append(nn.Linear(prev_size, output_size))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        """Defines Forward-Propagation."""
        return self.net(x)
