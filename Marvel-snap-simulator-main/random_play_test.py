# random_play_test.py
import random
from typing import List, Tuple

from simulator import GameState, legal_plays, apply_action, deepcopy_state
from factories import generate_all_cards
from location import generate_all_locations

# --- Initialize Card and Location Pools ---
ALL_CARDS = generate_all_cards()
ALL_LOCATIONS = generate_all_locations()

# --- Winner Evaluation (try import, else fallback) ---
try:
    from winconditions import evaluate_winner
except (ImportError, ModuleNotFoundError):
    def evaluate_winner(state: GameState) -> int:
        """Simple total-power comparison across all locations."""
        totals = [0, 0]
        for loc in state.board:
            for player in (0, 1):
                for cid in loc[player]:
                    totals[player] += ALL_CARDS[cid].power
        # Tie or higher total goes to player 0
        return 0 if totals[0] >= totals[1] else 1

# --- Helper Functions for Initialization ---

def draw_initial_hands_and_decks() -> Tuple[List[List[int]], List[List[int]]]:
    """Shuffle full card pool and deal 12-card hands to each player, rest as deck."""
    card_ids = list(range(len(ALL_CARDS)))
    random.shuffle(card_ids)
    hand0 = card_ids[:12]
    hand1 = card_ids[12:24]
    deck0 = card_ids[24:]
    deck1 = []  # Marvel Snap draws only initial hand
    return [hand0, hand1], [deck0, deck1]


def random_location_effects() -> List[int]:
    """Return a random selection of 3 distinct location indices."""
    indices = list(range(len(ALL_LOCATIONS)))
    random.shuffle(indices)
    return indices[:3]

# --- Simulation Loop ---

def initialize_state() -> GameState:
    hands, decks = draw_initial_hands_and_decks()
    board = [[[] for _ in range(2)] for _ in range(3)]
    effects = random_location_effects()
    return GameState(
        turn=1,
        energy=(1, 1),
        hand=hands,
        deck=decks,
        board=board,
        location_effects=effects
    )


def random_game() -> int:
    """Simulate one random game and return the winning player (0 or 1)."""
    state = initialize_state()
    while state.turn <= 6:
        for player in [0, 1]:
            actions = legal_plays(state, player)
            if actions:
                action = random.choice(actions)
                state = apply_action(state, player, action)
        # Advance turn & energy
        state = deepcopy_state(state)
        next_turn = state.turn + 1
        state.turn = next_turn
        state.energy = (next_turn, next_turn)
    return evaluate_winner(state)


def simulate(n_games: int = 1000):
    """Run n_games random simulations and print win counts."""
    results = {0: 0, 1: 0}
    for _ in range(n_games):
        w = random_game()
        results[w] += 1
    print(f"Simulation results over {n_games} games: {results}")

if __name__ == '__main__':
    simulate(500)
