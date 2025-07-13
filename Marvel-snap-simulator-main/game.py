import random
from loguru import logger
from factories import generate_all_cards
from factories import generate_all_locations
from ai import AIPlayer
from display import Displayer
from turn import Turn
from winconditions import WinConditions
from enums import PLAYER1_ID, PLAYER2_ID

class Game:
    def __init__(self):
        logger.info("Game initialization")
        # Generate card and location pools
        self.all_cards = generate_all_cards()
        self.all_locations = generate_all_locations()

        # Initialize players with MC enabled but hidden progress
        self.players = [
            AIPlayer(self, PLAYER1_ID, all_cards, use_mc=True, show_progress=False),
            AIPlayer(self, PLAYER2_ID, all_cards, use_mc=True, show_progress=False),
        ]

        # Prepare locations
        self.locations = random.sample(self.all_locations, 3)
        for idx, loc in enumerate(self.locations):
            loc.position = idx

        # Setup turn tracking
        self.current_turn = 0
        self.current_location = 0
        self.turn = Turn(self.current_turn, self)

        # Display helper
        self.displayer = Displayer(self.players, self.locations)

    def reveal_location(self):
        if self.current_location >= len(self.locations):
            return

        location = self.locations[self.current_location]
        logger.debug(
            f"Location revealed: {location} at position {self.current_location}"
        )
        location.revealed = True
        location.position = self.current_location
        self.locations[self.current_location] = location
        self.current_location += 1
        location.apply_location_effect(self)

    def generate_locations(self):
        return random.sample(self.all_locations, 3)

    def prepare_game(self):
        self.locations = self.generate_locations()
        self.reveal_location()
        for location in self.locations:
            location.position = self.locations.index(location)

    def apply_ongoing_abilities(self):
        for player_id in PLAYER1_ID, PLAYER2_ID:
            for location in self.locations:
                for card in location.cards:
                    self = card.ongoing(self)
            self.apply_location_effects(player_id)

    def apply_location_effects(self, player_id):
        player = self.players[player_id]
        for location_id, location in enumerate(self.locations):
            if location.effect and location.revealed:
                for card in location.cards:
                    if card.owner_id == player_id and not card.location_effect_applied:
                        location.effect(
                            card, player, location_id
                        )  # Pass location_id instead of location
                        card.location_effect_applied = (
                            True  # Set the flag after applying the effect
                        )

    def play_game(self):
        self.displayer.display_deck_and_hands()

        for turn_id in range(6):  # Loop through the 6 turns
            self.current_turn = turn_id
            self.turn = Turn(turn_id, self)
            logger.info(f"Turn {self.current_turn}")
            if 4 > self.current_turn > 1:
                self.reveal_location()
            self.turn.play_turn()
            self.turn.end_of_turn()
            self.displayer.display_game_state()

        WinConditions(self.locations, self.players).declare_winner()

    def play_game_remaining(self):
        """
        Continue playing from the current turn to turn 5 (inclusive) using AI decisions.
        This supports Monte Carlo rollouts without restarting the entire game.
        """
        # Starting from the next turn
        for t in range(self.current_turn + 1, 6):
            self.current_turn = t
            # Reveal a new location if it's turn 2 or 3
            if t in [1, 2]:  # zero-based turns: reveal at turns 1 and 2
                self.reveal_location()
            # Play a full turn
            self.turn.play_turn()
