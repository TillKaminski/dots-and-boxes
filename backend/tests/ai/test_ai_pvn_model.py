"""Tests for the PolicyValueNet Model."""

import pytest
import torch

from ai.model.pvn_model import PolicyValueNet

# Set Game Parameters
NUM_CHANNELS = 7
BOARD_SIZE = 4
NUM_ACTIONS = 40  # Horizontal (4 * 5) + Vertical (5 * 4) 
BATCH_SIZE = 4


@pytest.fixture
def create_test_model():
    """Set up standard parameters for the board game."""
    
    model = PolicyValueNet(NUM_CHANNELS, BOARD_SIZE, NUM_ACTIONS)

    # Create dummy input tensor: (Batch, Channels, Height, Width)
    dummy_input = torch.randn(
        BATCH_SIZE, NUM_CHANNELS, BOARD_SIZE, BOARD_SIZE
    )

    return model, dummy_input

def test_instantiation(create_test_model):
    """Test model creation."""
    model, _ = create_test_model
    assert isinstance(model, PolicyValueNet)

def test_forward_pass_output_shapes(create_test_model):
    """Test Output Shapes."""
    model, dummy_input = create_test_model
    policy_out, value_out = model(dummy_input)

    # Check Policy Output Shape
    expected_policy_shape = (BATCH_SIZE, NUM_ACTIONS)
    assert policy_out.shape == expected_policy_shape

    # Check Value Output Shape
    expected_value_shape = (BATCH_SIZE, 1)
    assert value_out.shape == expected_value_shape

def test_value_output_range(create_test_model):
    """Test that Value Head Output is between -1 and 1."""
    model, dummy_input = create_test_model
    _, value_out = model(dummy_input)
    
    # Check maximum is <= 1.0 (with small tolerance)
    max_val = value_out.max().item()
    assert max_val <= 1.0 + 1e-6 
    
    # Check minimum value is >= -1.0 (with small tolerance)
    min_val = value_out.min().item()
    assert min_val >= -1.0 - 1e-6 

def test_device_transfer(create_test_model):
    """Test if model can be transferred between devices (CPU/GPU)."""
    model, dummy_input = create_test_model

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Set device
    model_device = model.to(device)
    input_device = dummy_input.to(device)
    
    policy_out, value_out = model_device(input_device)
    
    # Check if outputs are on the correct device
    assert policy_out.device.type == device.type
    assert value_out.device.type == device.type
    
    # Check shapes
    expected_policy_shape = (BATCH_SIZE, NUM_ACTIONS)
    assert policy_out.shape == expected_policy_shape
    