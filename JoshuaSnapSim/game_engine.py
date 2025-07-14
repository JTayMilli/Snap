# marvel_snap_rl/game_engine.py

import random
from typing import List, Tuple

# Import our data structures, definitions, and the new ability resolver
from game_state import GameState, Player, Location, Card, PlayerId
from card_data import CARD_DEFINITIONS
from location_data import LOCATION_DEFINITIONS
from ability_resolver import AbilityResolver

class GameEngine:
    """
    Manages the core logic of a Marvel Snap game.
    This class is responsible for initializing the game, processing turns,
    resolving abilities, and determining the winner.
    """

    def __init__(self, player0_deck: List[str], player1_deck: List[str]):
        """
        Initializes the game engine with player decks.
        """
        self.player_decks = [player0_deck, player1_deck]
        self.game_state = self.setup_game()
        self.ability_resolver = AbilityResolver(self.game_state)

    def create_card_instance(self, card_id: str, owner: PlayerId) -> Card:
        """Creates a Card instance from a card_id."""
        card_def = CARD_DEFINITIONS[card_id]
        return Card(
            card_id=card_id,
            base_cost=card_def.cost,
            base_power=card_def.power,
            current_cost=card_def.cost,
            current_power=card_def.power,
            owner=owner
        )

    def setup_game(self) -> GameState:
        """
        Creates the initial GameState for a new game.
        """
        players = [Player(player_id=0), Player(player_id=1)]
        for i, deck_ids in enumerate(self.player_decks):
            deck = [self.create_card_instance(cid, owner=i) for cid in deck_ids]
            random.shuffle(deck)
            players[i].deck = deck

        location_ids = random.sample(list(LOCATION_DEFINITIONS.keys()), 3)
        locations = [Location(location_id=loc_id) for loc_id in location_ids]

        state = GameState(players=players, locations=locations)
        state.players[random.randint(0, 1)].has_priority = True

        for _ in range(3):
            state.get_player(0).draw_card()
            state.get_player(1).draw_card()
            
        self.apply_start_of_game_effects(state)
        return state

    def apply_start_of_game_effects(self, state: GameState):
        """Applies location effects that trigger at the start of the game."""
        # This is where we would implement logic for locations like 'Elysium'
        pass

    def process_turn(self, player0_plays: List[Tuple[int, int]], player1_plays: List[Tuple[int, int]]):
        """
        Processes a single turn of the game.
        Args:
            player0_plays: A list of (card_in_hand_idx, location_idx) tuples.
            player1_plays: A list of (card_in_hand_idx, location_idx) tuples.
        """
        state = self.game_state
        state.turn += 1
        for player in state.players:
            player.energy = state.turn
            player.draw_card()

        if state.turn <= 3:
            state.locations[state.turn - 1].is_revealed = True

        # Play cards and collect them for On Reveal resolution
        all_played_cards = []
        plays = [player0_plays, player1_plays]
        for player_id, player_plays in enumerate(plays):
            player = state.get_player(player_id)
            # Sort by index descending to avoid issues when popping from hand
            for card_idx, loc_idx in sorted(player_plays, key=lambda x: x[0], reverse=True):
                card = player.hand.pop(card_idx)
                card.location = loc_idx
                state.locations[loc_idx].cards[player_id].append(card)
                all_played_cards.append(card)

        # Reveal cards and trigger 'On Reveal' effects
        # A full implementation would sort `all_played_cards` based on priority
        self.ability_resolver.resolve_on_reveal_effects(all_played_cards)

        # Re-apply ongoing effects to update the board state after plays
        self.ability_resolver.apply_ongoing_effects()
        
        # Check for game end
        if state.turn >= 6:
            self.end_game()

    def calculate_location_power(self, location: Location, player_id: PlayerId) -> int:
        """Calculates the total power at a location for a player, considering all effects."""
        # Calculate the sum of power from cards, which already have ongoing effects applied
        power = sum(card.current_power for card in location.cards[player_id])

        # Apply location-wide doubling effects like Iron Man
        num_iron_man = sum(1 for card in location.cards[player_id] if card.card_id == "iron_man")
        if num_iron_man > 0:
            power *= (2 ** num_iron_man)
            
        # Here we would add other location-wide power modifications (e.g. from location abilities)
        return power

    def end_game(self):
        """Finalizes the game, calculates power, and determines the winner."""
        state = self.game_state
        state.game_over = True
        
        # Apply all ongoing effects one last time for final scoring
        self.ability_resolver.apply_ongoing_effects()

        player0_wins = 0
        player1_wins = 0
        
        for location in state.locations:
            p0_power = self.calculate_location_power(location, 0)
            p1_power = self.calculate_location_power(location, 1)

            if p0_power > p1_power:
                player0_wins += 1
            elif p1_power > p0_power:
                player1_wins += 1

        if player0_wins > player1_wins:
            state.winner = 0
        elif player1_wins > player0_wins:
            state.winner = 1
        else:
            p0_total_power = sum(self.calculate_location_power(loc, 0) for loc in state.locations)
            p1_total_power = sum(self.calculate_location_power(loc, 1) for loc in state.locations)
            if p0_total_power > p1_total_power:
                state.winner = 0
            elif p1_total_power > p0_total_power:
                state.winner = 1
            else:
                state.winner = -1 # Draw


if __name__ == '__main__':
    basic_deck = ["misty_knight", "shocker", "cyclops", "the_thing", "abomination", "hulk"] * 2
    engine = GameEngine(player0_deck=basic_deck, player1_deck=basic_deck)
    state = engine.game_state

    print("--- Game Setup ---")
    print(f"Player 0 Hand: {[card.card_id for card in state.get_player(0).hand]}")
    print(f"Locations: {[loc.location_id for loc in state.locations]}")
    
    # This is a placeholder for a full game loop.
    # In a real scenario, we would loop through turns 1-6,
    # get actions from players (or our RL agent), and call process_turn.
    # For example, on turn 1, player 0 plays the first card in their hand to location 0.
    # engine.process_turn(player0_plays=[(0, 0)], player1_plays=[])

    engine.end_game()
    print("\n--- Game Over ---")
    print(f"Winner: Player {engine.game_state.winner}")

