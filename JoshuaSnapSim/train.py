# marvel_snap_rl/train.py

import random
import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
from collections import deque
from typing import List, Tuple, NamedTuple
import os # Import the os module

# Import all our custom components
from game_engine import GameEngine
from state_vectorizer import StateVectorizer
from action_manager import ActionManager, END_TURN_ACTION_ID, NUM_ACTIONS
from neural_net import PolicyValueNet

# --- Configuration ---
class Config:
    NUM_TRAINING_GAMES = 5000
    REPLAY_BUFFER_SIZE = 10000
    BATCH_SIZE = 128
    LEARNING_RATE = 0.001
    SAVE_MODEL_EVERY_N_GAMES = 100

# --- Replay Buffer ---
class ReplayBuffer:
    """A simple buffer to store experiences for training."""
    def __init__(self, max_size):
        self.buffer = deque(maxlen=max_size)
    
    def add(self, experience):
        self.buffer.append(experience)
        
    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)
        
    def __len__(self):
        return len(self.buffer)

# A structure to hold a single training example
TrainingSample = NamedTuple('TrainingSample', [('state', np.ndarray), ('policy', np.ndarray), ('value', float)])

# --- Helper function to get policy from the network ---
def get_policy_from_net(net: PolicyValueNet, state_vector: np.ndarray, action_mask: np.ndarray) -> np.ndarray:
    """Gets the policy probabilities from the network for a given state."""
    obs_tensor = torch.from_numpy(state_vector).float().unsqueeze(0)
    with torch.no_grad():
        policy_logits, _ = net(obs_tensor)
    
    action_mask_tensor = torch.from_numpy(action_mask == 0).unsqueeze(0)
    masked_logits = policy_logits.masked_fill(action_mask_tensor, -1e9)
    policy_probs = F.softmax(masked_logits, dim=1).squeeze(0).numpy()
    return policy_probs

# --- Self-Play Function ---
def run_self_play_game(net: PolicyValueNet, vectorizer: StateVectorizer, action_manager: ActionManager) -> List[TrainingSample]:
    """
    Plays one full game of self-play using the provided network.
    This version correctly models the simultaneous turn structure of Marvel Snap.
    """
    starter_deck = ["wasp", "misty_knight", "shocker", "cyclops", "captain_america", "mr_fantastic", "iron_man", "hulk"] * 2
    random.shuffle(starter_deck)
    engine = GameEngine(player0_deck=starter_deck[:12], player1_deck=starter_deck[12:])
    state = engine.game_state
    
    game_history = []

    while not state.game_over:
        if state.turn > 6:
            engine.end_game()
            continue

        # --- Decide plays for BOTH players before processing the turn ---
        # Player 0 decides a move
        p0_obs = vectorizer.vectorize(state, 0)
        p0_mask = action_manager.get_action_mask(state, 0)
        p0_policy = get_policy_from_net(net, p0_obs, p0_mask)
        game_history.append({'player_id': 0, 'state': p0_obs, 'policy': p0_policy})
        p0_action = np.random.choice(NUM_ACTIONS, p=p0_policy)
        p0_play = action_manager.get_play_from_action_id(p0_action)
        
        # Player 1 decides a move
        p1_obs = vectorizer.vectorize(state, 1)
        p1_mask = action_manager.get_action_mask(state, 1)
        p1_policy = get_policy_from_net(net, p1_obs, p1_mask)
        game_history.append({'player_id': 1, 'state': p1_obs, 'policy': p1_policy})
        p1_action = np.random.choice(NUM_ACTIONS, p=p1_policy)
        p1_play = action_manager.get_play_from_action_id(p1_action)

        player0_plays = [p0_play] if p0_play else []
        player1_plays = [p1_play] if p1_play else []
        
        # --- Process the full turn with both players' moves ---
        engine.process_turn(player0_plays, player1_plays)

    # Game is over, assign outcomes to the stored experiences
    winner = state.winner
    training_samples = []
    for experience in game_history:
        player_id = experience['player_id']
        outcome = 0.0
        if winner != -1: # Not a draw
            outcome = 1.0 if player_id == winner else -1.0
        
        training_samples.append(
            TrainingSample(state=experience['state'], policy=experience['policy'], value=outcome)
        )
        
    return training_samples

# --- Training Step Function ---
def train_step(net: PolicyValueNet, optimizer: optim.Optimizer, batch: List[TrainingSample]):
    """Performs one step of training on a batch of data."""
    states, target_policies, target_values = zip(*batch)
    
    states_tensor = torch.from_numpy(np.array(states)).float()
    target_policies_tensor = torch.from_numpy(np.array(target_policies)).float()
    target_values_tensor = torch.from_numpy(np.array(target_values)).float().unsqueeze(1)
    
    # Forward pass
    pred_policy_logits, pred_values = net(states_tensor)
    
    # Calculate Loss
    value_loss = F.mse_loss(pred_values, target_values_tensor)
    policy_loss = F.cross_entropy(pred_policy_logits, target_policies_tensor)
    loss = value_loss + policy_loss
    
    # Backward pass and optimization
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    return loss.item()

# --- Main Training Loop ---
def main():
    config = Config()
    
    net = PolicyValueNet()
    optimizer = optim.Adam(net.parameters(), lr=config.LEARNING_RATE)
    replay_buffer = ReplayBuffer(max_size=config.REPLAY_BUFFER_SIZE)
    vectorizer = StateVectorizer()
    action_manager = ActionManager()

    # --- Create a dedicated folder for saved models ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, "saved_models")
    os.makedirs(models_dir, exist_ok=True)
    
    print("--- Starting Self-Play Training ---")
    
    for game_num in range(1, config.NUM_TRAINING_GAMES + 1):
        # 1. Generate data through self-play
        new_samples = run_self_play_game(net, vectorizer, action_manager)
        for sample in new_samples:
            replay_buffer.add(sample)
        
        # 2. Train the network if the buffer is ready
        if len(replay_buffer) >= config.BATCH_SIZE:
            batch = replay_buffer.sample(config.BATCH_SIZE)
            loss = train_step(net, optimizer, batch)
            
            if game_num % 10 == 0:
                print(f"Game: {game_num}, Loss: {loss:.4f}, Buffer Size: {len(replay_buffer)}")
        else:
            print(f"Game: {game_num}, Filling buffer... ({len(replay_buffer)}/{config.BATCH_SIZE})")
            
        # 3. Save the model periodically
        if game_num % config.SAVE_MODEL_EVERY_N_GAMES == 0:
            model_filename = f"marvel_snap_agent_v{game_num}.pth"
            model_path = os.path.join(models_dir, model_filename) # Save in the new folder
            torch.save(net.state_dict(), model_path)
            print(f"--- Model saved to {model_path} ---")

    print("--- Training Complete ---")

if __name__ == "__main__":
    main()
