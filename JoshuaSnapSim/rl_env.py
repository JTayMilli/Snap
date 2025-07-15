# marvel_snap_rl/rl_env.py

import numpy as np
from typing import List, Tuple, Dict, Any

from game_engine import GameEngine
from game_state import GameState, PlayerId
from state_vectorizer import StateVectorizer
from action_manager import ActionManager, NUM_ACTIONS, END_TURN_ACTION_ID

# A simple policy for the opponent AI
def random_policy(state: GameState, player_id: int, action_manager: ActionManager) -> List[Tuple[int, int]]:
    """A simple random policy for the opponent."""
    mask = action_manager.get_action_mask(state, player_id)
    valid_action_ids = np.where(mask == 1)[0]
    
    if len(valid_action_ids) == 0:
        return []

    # Just pick one random valid action to play
    chosen_action_id = np.random.choice(valid_action_ids)
    
    if chosen_action_id == END_TURN_ACTION_ID:
        return []
        
    play = action_manager.get_play_from_action_id(chosen_action_id)
    return [play] if play else []


class MarvelSnapEnv:
    """
    A Reinforcement Learning Environment for Marvel Snap, following the
    OpenAI Gym/Gymnasium API standard.
    """
    def __init__(self, deck1: List[str], deck2: List[str]):
        self.deck1 = deck1
        self.deck2 = deck2
        self.engine = GameEngine(self.deck1, self.deck2)
        self.vectorizer = StateVectorizer()
        self.action_manager = ActionManager()
        self.agent_player_id = 0 # The RL agent is always Player 0
        self.opponent_player_id = 1

    def reset(self) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Resets the environment to the beginning of a new game.
        Returns the initial observation and an info dictionary.
        """
        self.engine = GameEngine(self.deck1, self.deck2)
        state = self.engine.game_state
        
        obs = self.vectorizer.vectorize(state, self.agent_player_id)
        info = {
            "action_mask": self.action_manager.get_action_mask(state, self.agent_player_id)
        }
        return obs, info

    def step(self, action_id: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Takes an action and executes one turn of the game.
        Since this is a two-player game, this step involves the agent's move
        and the opponent's move.
        """
        agent_plays = []
        play = self.action_manager.get_play_from_action_id(action_id)
        if play:
            agent_plays.append(play)

        # Get opponent's move using the simple random policy
        opponent_plays = random_policy(self.engine.game_state, self.opponent_player_id, self.action_manager)
        
        # Process the turn
        self.engine.process_turn(
            player0_plays=agent_plays,
            player1_plays=opponent_plays
        )
        
        state = self.engine.game_state
        
        # Determine reward
        terminated = state.game_over
        reward = 0.0

        # --- REWARD SHAPING ---
        # Add a small penalty for passing the turn (i.e., not playing a card).
        # This encourages the agent to be active rather than learning a "lazy" policy.
        if not agent_plays:
            reward -= 0.01
        # ----------------------

        if terminated:
            if state.winner == self.agent_player_id:
                reward = 1.0  # Win
            elif state.winner == self.opponent_player_id:
                reward = -1.0 # Loss
            # If it's a draw, the reward will be 0.0 (or -0.01 if the agent passed on the last turn)

        # Get next state observation and info
        obs = self.vectorizer.vectorize(state, self.agent_player_id)
        info = {
            "action_mask": self.action_manager.get_action_mask(state, self.agent_player_id)
        }
        
        truncated = False
        
        return obs, reward, terminated, truncated, info

    def render(self):
        """Prints the current board state to the console."""
        print_board_state(self.engine.game_state, self.engine)

# This is a copy of the print function from main.py for standalone use if needed
def print_board_state(state: GameState, engine: GameEngine):
    """Utility function to print the current state of the board."""
    print("-" * 30)
    for i, location in enumerate(state.locations):
        p0_power = engine.calculate_location_power(location, 0)
        p1_power = engine.calculate_location_power(location, 1)
        
        p0_cards = [f"{card.card_id}({card.current_power})" for card in location.cards[0]]
        p1_cards = [f"{card.card_id}({card.current_power})" for card in location.cards[1]]
        
        print(f"Location {i}: {location.location_id} ({p0_power} vs {p1_power})")
        print(f"  Player 0: {p0_cards}")
        print(f"  Player 1: {p1_cards}")
    print("-" * 30)
