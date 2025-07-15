# marvel_snap_rl/neural_net.py

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

from typing import Tuple
from game_state import GameState, Location # Import GameState and Location
from state_vectorizer import StateVectorizer
from action_manager import NUM_ACTIONS

class PolicyValueNet(nn.Module):
    """
    The neural network for the RL agent.
    It takes a game state vector as input and outputs:
    1. A policy (probabilities for each possible action).
    2. A value (an estimate of the win probability from this state).
    """
    def __init__(self):
        super(PolicyValueNet, self).__init__()
        
        # First, we need to know the size of our input vector.
        # To do this, we create a dummy GameState object and vectorize it.
        vectorizer = StateVectorizer()
        # FIX: Create a more realistic dummy state with 3 locations to avoid IndexError.
        # We use "ruins" as a safe, neutral location defined in our data.
        dummy_locations = [Location(location_id="ruins") for _ in range(3)]
        dummy_game_state = GameState(locations=dummy_locations)
        input_size = len(vectorizer.vectorize(dummy_game_state, 0))

        # Shared layers: these process the raw game state
        self.fc1 = nn.Linear(input_size, 512)
        self.fc2 = nn.Linear(512, 256)

        # The two "heads" of the network
        
        # 1. The Policy Head: outputs a score for each possible action
        self.policy_head = nn.Linear(256, NUM_ACTIONS)

        # 2. The Value Head: outputs a single number (-1 for loss, 1 for win)
        self.value_head = nn.Linear(256, 1)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        The forward pass of the network.
        """
        # Pass through the shared layers
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))

        # Calculate policy logits (raw scores for each action)
        policy_logits = self.policy_head(x)
        
        # Calculate the value (estimated chance of winning)
        # We use tanh to squash the output to be between -1 and 1
        value = torch.tanh(self.value_head(x))
        
        return policy_logits, value

if __name__ == '__main__':
    from rl_env import MarvelSnapEnv
    
    # --- Example Usage ---
    
    # 1. Create the environment to get an initial observation
    starter_deck = ["wasp", "misty_knight", "shocker"] * 4
    env = MarvelSnapEnv(deck1=starter_deck, deck2=starter_deck)
    obs, info = env.reset()

    # 2. Create the neural network
    net = PolicyValueNet()
    print("--- Neural Network Architecture ---")
    print(net)

    # 3. Convert the observation (numpy array) to a PyTorch tensor
    obs_tensor = torch.from_numpy(obs).float().unsqueeze(0) # Add a batch dimension

    # 4. Pass the observation through the network
    # In training, we'd use the GPU if available: obs_tensor.to(device)
    policy_logits, value = net(obs_tensor)

    # 5. Apply the action mask and get probabilities
    action_mask = torch.from_numpy(info["action_mask"]).float().unsqueeze(0)
    # Set logits of invalid actions to a very small number
    masked_policy_logits = policy_logits.masked_fill(action_mask == 0, -1e9)
    # Use softmax to convert logits to probabilities
    policy_probs = F.softmax(masked_policy_logits, dim=1)

    print("\n--- Network Output Example ---")
    print(f"Input vector shape: {obs_tensor.shape}")
    print(f"Output Policy Logits shape: {policy_logits.shape}")
    print(f"Output Policy Probabilities shape: {policy_probs.shape}")
    print(f"Output Value: {value.item():.4f}")

    # The agent would then sample an action from these probabilities
    action = torch.multinomial(policy_probs, 1).item()
    print(f"\nAgent samples action: {action}")
