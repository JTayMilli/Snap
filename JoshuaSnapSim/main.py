# marvel_snap_rl/main.py

import random
import numpy as np
from typing import List, Tuple

from game_engine import GameEngine
from game_state import GameState, Player
from action_manager import ActionManager, END_TURN_ACTION_ID

def get_plays_from_mask(state: GameState, player_id: int, action_manager: ActionManager) -> List[Tuple[int, int]]:
    """
    A more realistic AI that uses the action mask to make random valid plays.
    It will select one or more valid moves to perform this turn.
    """
    player = state.get_player(player_id)
    plays = []
    
    # Create a copy of the hand to track which cards have been "played" this turn
    # This is important for multi-card plays
    available_hand_indices = list(range(len(player.hand)))

    while True:
        # We need to regenerate the mask each time we decide to play a card,
        # as our energy changes. A simpler approach for a random AI is to just
        # pick one valid move and end. For a smarter AI, we'd need a more
        # complex decision process.
        
        # For this random AI, let's just pick one valid action.
        mask = action_manager.get_action_mask(state, player_id)
        valid_action_ids = np.where(mask == 1)[0]

        if len(valid_action_ids) == 0 or END_TURN_ACTION_ID in valid_action_ids and random.random() < 0.3:
             # End turn if no moves left, or randomly decide to end
            break
        
        # Exclude end turn action for selection unless it's the only option
        play_actions = [aid for aid in valid_action_ids if aid != END_TURN_ACTION_ID]
        if not play_actions:
            break
            
        chosen_action_id = random.choice(play_actions)
        play = action_manager.get_play_from_action_id(chosen_action_id)
        
        if play:
            hand_idx, loc_idx = play
            card = player.hand[hand_idx]
            
            # Check if we can still afford it and if the card is available
            if card.current_cost <= player.energy and hand_idx in available_hand_indices:
                plays.append(play)
                player.energy -= card.current_cost
                available_hand_indices.remove(hand_idx)
            else:
                # Can't afford this combo, stop planning
                break
        else:
            # Should not happen if we exclude END_TURN_ACTION_ID
            break
            
    # Restore energy, the engine will handle deduction
    player.energy = state.turn
    return plays


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


def run_game():
    starter_deck = ["wasp", "misty_knight", "shocker", "cyclops", "captain_america", "mr_fantastic", "iron_man", "hulk"] * 2
    random.shuffle(starter_deck)
    
    engine = GameEngine(player0_deck=starter_deck[:12], player1_deck=starter_deck[12:])
    state = engine.game_state
    action_manager = ActionManager()

    print("--- NEW GAME ---")
    
    for turn in range(1, 7):
        print(f"\n--- Turn {turn} ---")
        state.get_player(0).energy = turn
        state.get_player(1).energy = turn
        
        player0_plays = get_plays_from_mask(state, 0, action_manager)
        player1_plays = get_plays_from_mask(state, 1, action_manager)
        
        print(f"Player 0 plays: {player0_plays}")
        print(f"Player 1 plays: {player1_plays}")

        engine.process_turn(player0_plays, player1_plays)
        print_board_state(state, engine)

    print("\n--- GAME OVER ---")
    if state.winner == -1:
        print("Result: It's a Draw!")
    else:
        print(f"Result: Player {state.winner} wins!")

if __name__ == "__main__":
    run_game()
