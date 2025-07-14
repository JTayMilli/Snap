# marvel_snap_rl/action_manager.py

import numpy as np
from typing import List, Tuple, Optional

from game_state import GameState, Player, HAND_SIZE, LOCATION_COUNT, CARDS_PER_LOCATION

# --- Action Space Definition ---
# We define a fixed-size action space. An action is either playing a card
# from a specific hand slot to a specific location, or ending the turn.
# Total Actions = (Max Hand Size * Num Locations) + 1 (for End Turn)

NUM_ACTIONS = (HAND_SIZE * LOCATION_COUNT) + 1
END_TURN_ACTION_ID = NUM_ACTIONS - 1

class ActionManager:
    """
    Manages the action space and valid action masking.
    """
    def __init__(self):
        pass

    def get_action_mask(self, state: GameState, player_id: int) -> np.ndarray:
        """
        Generates a mask of valid actions for the given player.
        Returns a numpy array of 0s and 1s.
        """
        player = state.get_player(player_id)
        mask = np.zeros(NUM_ACTIONS, dtype=np.int8)

        # 1. Check 'Play Card' actions
        for hand_idx in range(HAND_SIZE):
            if hand_idx < len(player.hand):
                card = player.hand[hand_idx]
                # Check if player can afford the card
                if card.current_cost <= player.energy:
                    for loc_idx in range(LOCATION_COUNT):
                        location = state.locations[loc_idx]
                        # Check if the location is not full
                        if len(location.cards[player_id]) < CARDS_PER_LOCATION:
                            action_id = self.get_action_id(hand_idx, loc_idx)
                            mask[action_id] = 1
        
        # 2. 'End Turn' action is always valid
        mask[END_TURN_ACTION_ID] = 1
        
        return mask

    def get_action_id(self, hand_idx: int, location_idx: int) -> int:
        """Converts a (hand_idx, location_idx) pair to a unique action ID."""
        return hand_idx * LOCATION_COUNT + location_idx

    def get_play_from_action_id(self, action_id: int) -> Optional[Tuple[int, int]]:
        """Converts an action ID back to a (hand_idx, location_idx) pair."""
        if action_id == END_TURN_ACTION_ID:
            return None
        
        hand_idx = action_id // LOCATION_COUNT
        location_idx = action_id % LOCATION_COUNT
        return (hand_idx, location_idx)

if __name__ == '__main__':
    from game_engine import GameEngine

    # 1. Setup a game
    starter_deck = ["wasp", "misty_knight", "shocker", "cyclops", "hulk"] * 3
    engine = GameEngine(player0_deck=starter_deck[:12], player1_deck=starter_deck[12:])
    game_state = engine.game_state
    game_state.turn = 4
    game_state.get_player(0).energy = 4

    # 2. Create the manager
    action_manager = ActionManager()

    # 3. Get the valid action mask for Player 0
    valid_actions_mask = action_manager.get_action_mask(game_state, 0)

    print("--- Action Masking Example ---")
    print(f"Game State: Turn {game_state.turn}, Player 0 Energy: {game_state.get_player(0).energy}")
    print(f"Player 0 Hand: {[f'{c.card_id}({c.current_cost})' for c in game_state.get_player(0).hand]}")
    print(f"\nTotal possible actions: {NUM_ACTIONS}")
    print(f"Valid action mask (1s are legal moves):")
    print(valid_actions_mask)

    # 4. Find and print the human-readable valid actions
    valid_action_ids = np.where(valid_actions_mask == 1)[0]
    print("\nReadable valid actions:")
    for action_id in valid_action_ids:
        play = action_manager.get_play_from_action_id(action_id)
        if play:
            hand_idx, loc_idx = play
            card = game_state.get_player(0).hand[hand_idx]
            print(f"  - Play '{card.card_id}' (from hand slot {hand_idx}) to location {loc_idx}")
        else:
            print("  - End Turn")
