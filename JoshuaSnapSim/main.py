# marvel_snap_rl/main.py

import random
import numpy as np
import torch
import torch.nn.functional as F
import os # Import the os module

# Import our components
from rl_env import MarvelSnapEnv
from action_manager import END_TURN_ACTION_ID
from neural_net import PolicyValueNet

# --- Get the script's directory to build a robust path ---
script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(script_dir, "saved_models")

# --- CONFIGURATION TO LOAD THE TRAINED MODEL ---
# Specify just the filename of the trained model you want to use.
MODEL_FILENAME = "marvel_snap_agent_v5000.pth" 
TRAINED_MODEL_PATH = os.path.join(models_dir, MODEL_FILENAME)

def run_game_with_ai():
    """
    Initializes and runs a single game using a TRAINED Policy-Value Network
    to make decisions.
    """
    # Define decks for the players
    starter_deck = [
        "wasp", "misty_knight", "shocker", "cyclops", 
        "captain_america", "mr_fantastic", "iron_man", "hulk"
    ] * 2
    random.shuffle(starter_deck)
    
    # 1. Initialize the Environment and the AI Network
    env = MarvelSnapEnv(deck1=starter_deck[:12], deck2=starter_deck[12:])
    ai_net = PolicyValueNet()

    # --- LOAD THE TRAINED WEIGHTS ---
    if os.path.exists(TRAINED_MODEL_PATH):
        print(f"Loading trained model from: {TRAINED_MODEL_PATH}")
        ai_net.load_state_dict(torch.load(TRAINED_MODEL_PATH))
    else:
        print(f"WARNING: Model file not found at '{TRAINED_MODEL_PATH}'.")
        print("Running with an untrained, random AI.")
    
    # Set the network to evaluation mode (important for inference)
    ai_net.eval()
    # --------------------------------

    # 2. Reset the environment
    obs, info = env.reset()
    terminated = False
    total_reward = 0

    print("\n--- NEW GAME (RUN WITH TRAINED AI) ---")
    env.render()
    
    # 3. Main Game Loop
    while not terminated:
        print(f"\n--- Turn {env.engine.game_state.turn} ---")
        
        # --- AI Decision Making ---
        obs_tensor = torch.from_numpy(obs).float().unsqueeze(0)
        action_mask = torch.from_numpy(info["action_mask"]).float().unsqueeze(0)
        
        with torch.no_grad(): # No need for gradients during inference
            policy_logits, value_estimate = ai_net(obs_tensor)
            
        masked_logits = policy_logits.masked_fill(action_mask == 0, -1e9)
        policy_probs = F.softmax(masked_logits, dim=1)
        
        # Instead of sampling, for evaluation we usually take the best move
        action = torch.argmax(policy_probs).item()
        
        # 4. Take a step in the environment
        obs, reward, terminated, truncated, info = env.step(action)
        
        total_reward += reward
        
        print(f"AI (Player 0) chose action: {action} (Est. Win Chance: {value_estimate.item():.2f})")
        env.render()

    # 5. Print Final Result
    print("\n--- GAME OVER ---")
    print(f"Final Reward for AI: {total_reward}")

if __name__ == "__main__":
    run_game_with_ai()
