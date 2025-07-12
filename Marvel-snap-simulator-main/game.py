import random
from typing import TYPE_CHECKING, List, Optional

from loguru import logger

# Reverted to top-level imports as circular dependencies are resolved
from ai import AIPlayer
from data import ALL_CARDS, ALL_LOCATIONS
from enums import GameState, LOR, Player, Zone
from location import Location
from player import Player as HumanPlayer
from turn import Turn
from winconditions import determine_winner

if TYPE_CHECKING:
    from cards import Card


class Game(object):
    def __init__(self, player1_deck: List[str], player2_deck: List[str], player1_is_ai: bool = False, player2_is_ai: bool = True) -> None:
        self.player1_deck = player1_deck
        self.player2_deck = player2_deck
        self.player1_is_ai = player1_is_ai
        self.player2_is_ai = player2_is_ai
        self.turn = 0
        self.state = GameState.PRE_GAME
        self.locations: List[Location] = []

        # create players
        if self.player1_is_ai:
            self.player1 = AIPlayer(self.player1_deck, player_id=Player.PLAYER_1)
        else:
            self.player1 = HumanPlayer(self.player1_deck, player_id=Player.PLAYER_1)

        if self.player2_is_ai:
            self.player2 = AIPlayer(self.player2_deck, player_id=Player.PLAYER_2)
        else:
            self.player2 = HumanPlayer(self.player2_deck, player_id=Player.PLAYER_2)
        
        self.player1.game = self
        self.player2.game = self
        self.player1.opponent = self.player2
        self.player2.opponent = self.player1

    def setup(self):
        self.state = GameState.IN_PROGRESS
        # setup locations
        self.locations = self.get_locations()
        # give locations a reference to the game
        for location in self.locations:
            location.game = self

        # draw cards
        for _ in range(3):
            self.player1.draw_card()
            self.player2.draw_card()

    def get_locations(self) -> List[Location]:
        # get 3 random locations
        locations = random.sample(ALL_LOCATIONS, 3)
        # return a list of location objects
        return [location() for location in locations]

    def get_all_cards(self, zone: Optional[Zone] = None, player: Optional[Player] = None) -> List["Card"]:
        cards = []
        for location in self.locations:
            cards.extend(location.get_cards(player=player))
        cards.extend(self.player1.get_cards(zone=zone))
        cards.extend(self.player2.get_cards(zone=zone))
        return cards

    def get_random_card(self) -> "Card":
        return random.choice(ALL_CARDS)()

    def play(self) -> None:
        self.setup()
        while self.state == GameState.IN_PROGRESS:
            self.play_turn()
        self.end_game()

    def play_turn(self) -> None:
        self.turn += 1
        turn = Turn(self, self.turn, self.player1, self.player2)
        turn.play() # This will log the board state via display.py
        if self.turn >= 6:
            self.state = GameState.ENDED

    def end_game(self) -> None:
        logger.info("--- End of Game ---")
        # determine winner
        winner = determine_winner(self.player1, self.player2, self.locations)
        if winner == LOR.TIE:
            logger.info("RESULT:Tie")
        else:
            logger.info(f"RESULT:Player {winner.value} wins")

