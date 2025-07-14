# marvel_snap_rl/state_vectorizer.py

import numpy as np
from typing import List

from game_state import GameState, PlayerId, CARDS_PER_LOCATION, HAND_SIZE, LOCATION_COUNT
from card_data import CARD_DEFINITIONS
from location_data import LOCATION_DEFINITIONS

class StateVectorizer:
    """
    Translates a GameState object into a numerical vector for a neural network.
    The vector is created from the perspective of a specific player.
    """
    def __init__(self):
        # Create mappings from string IDs to integer indices for one-hot encoding.
        # This ensures that each card and location has a consistent place in the vector.
        self.card_to_idx = {card_id: i for i, card_id in enumerate(CARD_DEFINITIONS.keys())}
        self.location_to_idx = {loc_id: i for i, loc_id in enumerate(LOCATION_DEFINITIONS.keys())}
        self.num_cards = len(CARD_DEFINITIONS)
        self.num_locations = len(LOCATION_DEFINITIONS)

    def vectorize(self, state: GameState, player_id: PlayerId) -> np.ndarray:
        """
        Creates the numerical vector for the given game state and player.
        """
        player = state.get_player(player_id)
        opponent = state.get_opponent(player_id)
        
        # --- Player and Game Info (Global State) ---
        # Turn (1-6), Energy, Hand Size, Deck Size
        player_info = [
            state.turn,
            player.energy,
            len(player.hand),
            len(player.deck)
        ]
        
        # --- Opponent Info ---
        # Opponent Hand Size, Deck Size
        opponent_info = [
            len(opponent.hand),
            len(opponent.deck)
        ]

        # --- Hand Features ---
        # One-hot encoding of cards in hand. A vector of 0s with a 1 for each card held.
        hand_vector = np.zeros(self.num_cards, dtype=np.float32)
        for card in player.hand:
            hand_vector[self.card_to_idx[card.card_id]] = 1
            
        # --- Location and Card-on-Board Features ---
        location_features = []
        for i in range(LOCATION_COUNT):
            location = state.locations[i]
            
            # Location ID (one-hot)
            loc_identity = np.zeros(self.num_locations, dtype=np.float32)
            loc_identity[self.location_to_idx[location.location_id]] = 1
            location_features.extend(loc_identity)
            
            # Cards at this location
            for p_id in [player_id, 1 - player_id]: # Player's cards first, then opponent's
                cards_at_loc = location.cards[p_id]
                for j in range(CARDS_PER_LOCATION):
                    if j < len(cards_at_loc):
                        card = cards_at_loc[j]
                        # Card ID (one-hot), current power, current cost, is_revealed
                        card_identity = np.zeros(self.num_cards, dtype=np.float32)
                        card_identity[self.card_to_idx[card.card_id]] = 1
                        card_features = [card.current_power, card.current_cost, float(card.is_revealed)]
                        location_features.extend(card_identity)
                        location_features.extend(card_features)
                    else:
                        # If no card, add placeholder zeros
                        location_features.extend(np.zeros(self.num_cards + 3, dtype=np.float32))

        # --- Combine all features into a single flat vector ---
        final_vector = np.concatenate([
            np.array(player_info, dtype=np.float32),
            np.array(opponent_info, dtype=np.float32),
            hand_vector,
            np.array(location_features, dtype=np.float32)
        ]).flatten()
        
        return final_vector

if __name__ == '__main__':
    # Example of how to use the StateVectorizer
    from game_engine import GameEngine

    # 1. Setup a game
    starter_deck = ["wasp", "misty_knight", "shocker", "cyclops", "hulk"] * 3
    engine = GameEngine(player0_deck=starter_deck[:12], player1_deck=starter_deck[12:])
    game_state = engine.game_state
    
    # 2. Create the vectorizer
    vectorizer = StateVectorizer()
    
    # 3. Vectorize the state for Player 0
    player0_pov_vector = vectorizer.vectorize(game_state, 0)
    
    print("--- State Vectorization Example ---")
    print(f"Vectorizing the initial game state for Player 0.")
    print(f"Total length of the state vector: {len(player0_pov_vector)}")
    print("\nFirst 20 elements of the vector:")
    print(player0_pov_vector[:20])
    
    # You can see the first few elements match our game state:
    # Turn (1), Energy (0), Hand Size (3), Deck Size (9), Opp Hand (3), Opp Deck (9), etc.
