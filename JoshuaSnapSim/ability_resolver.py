# marvel_snap_rl/ability_resolver.py

from typing import Dict, Callable, List
from game_state import GameState, Card, PlayerId
from card_data import CARD_DEFINITIONS

class AbilityResolver:
    """
    Handles the resolution of all card and location abilities.
    This class uses a dispatcher pattern to map ability names to their
    corresponding logic.
    """

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        
        # --- Dispatchers for Card Abilities ---
        self.on_reveal_dispatcher: Dict[str, Callable] = {
            "sentinel": self._on_reveal_sentinel,
            "medusa": self._on_reveal_medusa,
            "carnage": self._on_reveal_carnage,
            # Add other 'On Reveal' card_ids and their functions here
        }

        self.ongoing_dispatcher: Dict[str, Callable] = {
            "captain_america": self._ongoing_captain_america,
            "iron_man": self._ongoing_iron_man,
            # Add other 'Ongoing' card_ids and their functions here
        }

    def resolve_on_reveal_effects(self, cards_played_this_turn: List[Card]):
        """
        Resolves 'On Reveal' effects for cards played this turn, respecting priority.
        """
        # A full implementation would sort cards_played_this_turn based on player priority
        # and play order. For now, we iterate through them.
        for card in cards_played_this_turn:
            if card.card_id in self.on_reveal_dispatcher:
                # Check for 'Knowhere' location effect
                location = self.game_state.locations[card.location]
                if location.location_id != "knowhere":
                    self.on_reveal_dispatcher[card.card_id](card)
                    card.ability_used = True

    def apply_ongoing_effects(self):
        """
        Applies all 'Ongoing' effects from cards on the board.
        This should be called whenever the game state changes to recalculate powers.
        """
        # First, reset all card powers to their base power to avoid stacking effects
        for location in self.game_state.locations:
            for player_cards in location.cards:
                for card in player_cards:
                    card.current_power = card.base_power

        # Apply ongoing effects from all cards in play
        for location in self.game_state.locations:
            for player_cards in location.cards:
                for card in player_cards:
                    if card.card_id in self.ongoing_dispatcher:
                        self.ongoing_dispatcher[card.card_id](card)

    # --- On Reveal Ability Implementations ---

    def _on_reveal_sentinel(self, card: Card):
        """On Reveal: Add another Sentinel to your hand."""
        player = self.game_state.get_player(card.owner)
        if len(player.hand) < 7: # Max hand size
            sentinel_def = CARD_DEFINITIONS["sentinel"]
            new_sentinel = Card(
                card_id="sentinel",
                base_cost=sentinel_def.cost,
                base_power=sentinel_def.power,
                current_cost=sentinel_def.cost,
                current_power=sentinel_def.power,
                owner=card.owner
            )
            player.hand.append(new_sentinel)

    def _on_reveal_medusa(self, card: Card):
        """On Reveal: If this is at the middle location, +2 Power."""
        if card.location == 1: # Middle location
            card.current_power += 2

    def _on_reveal_carnage(self, card: Card):
        """On Reveal: Destroy your other cards here. +2 Power for each card destroyed."""
        location = self.game_state.locations[card.location]
        player = self.game_state.get_player(card.owner)
        
        cards_at_location = list(location.cards[card.owner])
        destroyed_count = 0
        for other_card in cards_at_location:
            if other_card is not card:
                # A real implementation would check for "Wakanda" or Armor's protection
                location.cards[card.owner].remove(other_card)
                player.discard.append(other_card) # Or a 'destroyed' pile
                destroyed_count += 1
        
        card.current_power += 2 * destroyed_count

    # --- Ongoing Ability Implementations ---

    def _ongoing_captain_america(self, card: Card):
        """Ongoing: Your other cards at this location have +1 Power."""
        location = self.game_state.locations[card.location]
        for other_card in location.cards[card.owner]:
            if other_card is not card:
                other_card.current_power += 1

    def _ongoing_iron_man(self, card: Card):
        """Ongoing: Your total Power is doubled at this Location."""
        # This is a tricky one. It needs to be applied *after* all other power boosts.
        # A more robust engine would have different phases for Ongoing effects.
        # For now, we can handle it in the get_total_power calculation.
        # This is a placeholder to show the mapping.
        pass


if __name__ == '__main__':
    # This file is not meant to be run directly.
    # It will be imported and used by the GameEngine.
    print("Ability Resolver - Contains logic for card and location abilities.")
    print("This module is intended to be used by the GameEngine.")

