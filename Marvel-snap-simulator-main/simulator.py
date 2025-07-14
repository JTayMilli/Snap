# simulator.py
from dataclasses import dataclass, field
from typing import List, Tuple
import copy

# Import your existing card and location definitions
from factories import generate_all_cards
from location import generate_all_locations

# --- Global Pools ---
# A list of Card instances; card_id is index into this list
ALL_CARDS = generate_all_cards()
# A list of Location instances; location_id is index into this list
ALL_LOCATIONS = generate_all_locations()
# Ensure each Location knows its index for effect dispatch
for idx, loc in enumerate(ALL_LOCATIONS):
    loc.position = idx

@dataclass
class GameState:
    turn: int                               # current turn (1–6)
    energy: Tuple[int, int]                # energy for [player0, player1]
    hand: List[List[int]]                  # card IDs in hand per player
    deck: List[List[int]]                  # remaining deck IDs per player
    board: List[List[List[int]]]           # board[location][player] -> list of card IDs
    location_effects: List[int] = field(default_factory=list)  # indices into ALL_LOCATIONS

@dataclass
class Action:
    card_id: int
    location_id: int

# --- Helper Implementations ---

def get_card_cost(card_id: int) -> int:
    """Return the energy cost for a given card ID."""
    return ALL_CARDS[card_id].energy_cost


def can_play_to_location(card_id: int, loc: int, state: GameState, player: int) -> bool:
    """Return True if `player` can play `card_id` to location `loc` in `state`."""
    # Max 4 cards per player per location
    if len(state.board[loc][player]) >= 4:
        return False
    # Location-specific play restrictions
    loc_idx = state.location_effects[loc]
    location = ALL_LOCATIONS[loc_idx]
    # Some locations define can_play_card(self, turn)
    if hasattr(location, 'can_play_card'):
        if not location.can_play_card(location, state.turn):
            return False
    return True


def resolve_effects(state: GameState, player: int, action: Action):
    """Apply location and card effects triggered by this action."""
    card = ALL_CARDS[action.card_id]
    # 1) Apply location's on-play effect if defined
    loc_idx = state.location_effects[action.location_id]
    location = ALL_LOCATIONS[loc_idx]
    if hasattr(location, 'effect') and location.effect:
        try:
            location.effect(card, player, action.location_id, state)
        except TypeError:
            location.effect(card, player, action.location_id)

    # 2) Apply the card's own reveal effect (On-Reveal)
    if hasattr(card, 'reveal'):
        try:
            card.reveal(state, player, action.location_id)
        except TypeError:
            card.reveal(player, action.location_id, state)

    # 3) Apply card's ongoing effect if it exists
    if hasattr(card, 'ongoing'):
        try:
            card.ongoing(state)
        except Exception:
            pass

    # 4) Trigger any on-any-card-reveal effects on other cards at this location
    for other_id in state.board[action.location_id][player]:
        if other_id == action.card_id:
            continue
        other_card = ALL_CARDS[other_id]
        if hasattr(other_card, 'on_any_card_reveal_effect'):
            try:
                other_card.on_any_card_reveal_effect(state, player, action.location_id, card)
            except TypeError:
                other_card.on_any_card_reveal_effect(player, action.location_id, card)


def deepcopy_state(state: GameState) -> GameState:
    """Deep copy of GameState for branch simulations."""
    return copy.deepcopy(state)

# --- Core Simulator Functions ---

def legal_plays(state: GameState, player: int) -> List[Action]:
    """Return all legal plays for `player` in `state` as a list of Actions."""
    plays: List[Action] = []
    cur_energy = state.energy[player]
    for card_id in list(state.hand[player]):
        cost = get_card_cost(card_id)
        if cost > cur_energy:
            continue
        for loc in range(len(state.board)):
            if can_play_to_location(card_id, loc, state, player):
                plays.append(Action(card_id, loc))
    return plays


def apply_action(state: GameState, player: int, action: Action) -> GameState:
    """Return a new GameState reflecting `player` playing `action`."""
    new_state = deepcopy_state(state)
    # Remove the card from player's hand
    new_state.hand[player].remove(action.card_id)
    # Deduct energy
    cost = get_card_cost(action.card_id)
    e0, e1 = new_state.energy
    if player == 0:
        new_state.energy = (e0 - cost, e1)
    else:
        new_state.energy = (e0, e1 - cost)
    # Place card on board
    new_state.board[action.location_id][player].append(action.card_id)
    # Resolve any triggered effects
    resolve_effects(new_state, player, action)
    return new_state
