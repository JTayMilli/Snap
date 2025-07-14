# marvel_snap_rl/game_state.py

import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# --- Constants ---
MAX_ENERGY = 6
MAX_TURNS = 6
HAND_SIZE = 7
DECK_SIZE = 12
LOCATION_COUNT = 3
CARDS_PER_LOCATION = 4

# --- Enums and Basic Types ---
PlayerId = int  # 0 or 1

@dataclass
class Card:
    """
    Represents a single card instance in the game.
    This is a lightweight data structure. The logic for the card's ability
    is handled separately in the game_logic.py file.
    """
    card_id: str  # e.g., "iron_man", "sentinel"
    base_cost: int
    base_power: int
    current_cost: int
    current_power: int
    is_revealed: bool = False
    ability_used: bool = False
    owner: Optional[PlayerId] = None
    location: Optional[int] = None # 0, 1, 2

@dataclass
class Location:
    """
    Represents a single location on the board.
    """
    location_id: str # e.g., "xandar", "mirror_dimension"
    cards: List[List[Optional[Card]]] = field(default_factory=lambda: [[] for _ in range(2)]) # [player0_cards, player1_cards]
    is_revealed: bool = False

    def get_total_power(self, player_id: PlayerId) -> int:
        """Calculates the total power at this location for a given player."""
        return sum(card.current_power for card in self.cards[player_id])

@dataclass
class Player:
    """
    Represents a player's state.
    """
    player_id: PlayerId
    energy: int = 0
    deck: List[Card] = field(default_factory=list)
    hand: List[Card] = field(default_factory=list)
    discard: List[Card] = field(default_factory=list)
    has_priority: bool = False

    def draw_card(self):
        """Moves a card from the deck to the hand, if possible."""
        if self.deck and len(self.hand) < HAND_SIZE:
            self.hand.append(self.deck.pop(0))

@dataclass
class GameState:
    """
    Represents the entire state of the game at a single point in time.
    This object is designed to be easily copied and manipulated.
    """
    turn: int = 1
    players: List[Player] = field(default_factory=lambda: [Player(player_id=0), Player(player_id=1)])
    locations: List[Location] = field(default_factory=list)
    game_over: bool = False
    winner: Optional[PlayerId] = None # Can also be -1 for a draw

    def get_player(self, player_id: PlayerId) -> Player:
        return self.players[player_id]

    def get_opponent(self, player_id: PlayerId) -> Player:
        return self.players[1 - player_id]

    def clone(self) -> 'GameState':
        """
        Creates a deep copy of the game state. This is essential for MCTS
        and other lookahead algorithms, but we will aim to make it efficient.
        A more optimized version would avoid deepcopying everything.
        For now, this is a placeholder for a more optimized clone method.
        """
        # A simple, but potentially slow, way to deepcopy
        # In the future, we can write a custom, more performant clone method.
        from copy import deepcopy
        return deepcopy(self)

# --- Example Usage ---
if __name__ == '__main__':
    # This demonstrates how to create and manipulate the game state.
    
    # 1. Create cards
    # In a real scenario, these would be loaded from a central card data file.
    cyclops = Card(card_id="cyclops", base_cost=3, base_power=4, current_cost=3, current_power=4)
    iron_man = Card(card_id="iron_man", base_cost=5, base_power=0, current_cost=5, current_power=0)

    # 2. Create players and decks
    player1 = Player(player_id=0)
    player1.deck = [cyclops for _ in range(DECK_SIZE)]
    random.shuffle(player1.deck)

    player2 = Player(player_id=1)
    player2.deck = [iron_man for _ in range(DECK_SIZE)]
    random.shuffle(player2.deck)

    # 3. Create locations
    # In a real scenario, these would be chosen randomly from a location data file.
    locations = [Location(location_id="new_york"), Location(location_id="wakanda"), Location(location_id="asgard")]

    # 4. Create the initial game state
    initial_state = GameState(players=[player1, player2], locations=locations)
    initial_state.players[0].has_priority = True

    # 5. Simulate drawing starting hands
    for _ in range(3):
        initial_state.get_player(0).draw_card()
        initial_state.get_player(1).draw_card()

    print("--- Initial Game State ---")
    print(f"Turn: {initial_state.turn}")
    print(f"Player 1 Hand: {[card.card_id for card in initial_state.get_player(0).hand]}")
    print(f"Player 2 Hand: {[card.card_id for card in initial_state.get_player(1).hand]}")
    print(f"Locations: {[loc.location_id for loc in initial_state.locations]}")

