import torch.nn as nn
import torch.nn.functional as F
import torch


class PolicyValueNet(nn.Module):
    """Policy-Value Network. Takes Game State as input, outputs: policy (move probabilities),
    value (expected game result).
    """
    def __init__(self, num_channels: int, board_size: int, num_actions: int):
        """Model Constructor.
        
        ### Args:
        - **num_channels** (int): Number of Feature Planes.
        - **board_size** (int): Size of the Game Board.
        - **num_actions** (int): Number of possible moves.
        """
        super().__init__()
        
        self.board_size = board_size
        
        # Initial Convolutional Layer
        self.conv_in = nn.Conv2d(
            in_channels=num_channels, out_channels=128, kernel_size=3, padding=1
        )
        self.bn_in = nn.BatchNorm2d(128)
        
        # TODO: Add Residual Blocks
        # self.res_block1 = ResidualBlock(...)
        
        # Policy Head
        self.conv_policy = nn.Conv2d(in_channels=128, out_channels=2, kernel_size=1)
        self.bn_policy = nn.BatchNorm2d(2)
        
        # Linear layer to map flattened features to the action space
        self.fc_policy = nn.Linear(2 * board_size * board_size, num_actions)
        
        # Value Head
        self.conv_value = nn.Conv2d(in_channels=128, out_channels=1, kernel_size=1)
        self.bn_value = nn.BatchNorm2d(1)
        
        self.fc_value1 = nn.Linear(board_size * board_size, 64)
        
        #Output Linear layer (single scalar value)
        self.fc_value2 = nn.Linear(64, 1)

    def forward(self, x: torch.Tensor):
        """
        Calculates the policy logits and the predicted game value.
        
        ### Args:
        - **x** (torch.Tensor): Input batch of game states (Batch, C, H, W).
        
        ### Returns:
        - **policy_output** (torch.Tensor): Logits for all possible moves.
        - **value_output** (torch.Tensor): Predicted Game Result (scalar).
        """
        shared_features = F.relu(self.bn_in(self.conv_in(x)))
        # TODO: Add Residual Blocks
        # shared_features = self.res_block1(shared_features)
        
        # Evaluate Policy Head
        policy_head = F.relu(self.bn_policy(self.conv_policy(shared_features)))
        policy_head = policy_head.view(policy_head.size(0), -1) 
        policy_output = self.fc_policy(policy_head) 

        # Evaluate Value Head
        value_head = F.relu(self.bn_value(self.conv_value(shared_features)))
        value_head = value_head.view(value_head.size(0), -1)
        value_head = F.relu(self.fc_value1(value_head))

        # Use tanh() for Activation
        value_output = torch.tanh(self.fc_value2(value_head))

        return policy_output, value_output
    