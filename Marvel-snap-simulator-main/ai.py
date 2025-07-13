import random
import itertools
import copy
from loguru import logger
from winconditions import WinConditions
from enums import Winner

class AIPlayer:
    def __init__(self, game, player_id, all_cards, use_mc=False, show_progress=False):
        self.game = game
        self.player_id = player_id
        self.energy = 1
        self.turn_energy_spent = 0
        # Flag: enable Monte Carlo rollouts
        self.use_mc = use_mc
        # Flag: display progress output during MC
        self.show_progress = show_progress
        # Heuristic weights
        self.heuristic_weights = {
            'power_diff': 1.0,
            'xandar_bonus': 0.5,
            'no_destroy_bonus': 0.2,
        }
        # Monte Carlo parameters
        self.mc_params = {
            'top_k': 3,
            'rollouts': 20
        }
        # Deck & hand setup
        self.deck = self.draw_starting_deck(all_cards)
        self.starting_deck = copy.deepcopy(self.deck)
        self.discard_stack = []
        self.hand = self.draw_starting_hand(self.deck)
        self.played_cards = []

    def choose_plays(self):
        # STEP 1: enumerate legal play options
        play_options = []
        for card in self.hand:
            if card.energy_cost > self.energy:
                continue
            for loc in self.game.locations:
                if loc.can_play_card_at_location(card, loc, self.game.current_turn, self.energy):
                    play_options.append((card, loc.position))

        # STEP 2: build valid combos
        combos = []
        for r in range(len(play_options) + 1):
            for combo in itertools.combinations(play_options, r):
                cards = [c for c, _ in combo]
                if len(set(cards)) != len(cards):
                    continue
                if sum(c.energy_cost for c in cards) > self.energy:
                    continue
                combos.append(combo)

        # STEP 3: heuristic evaluation
        scored = [(self.evaluate_sequence(c), c) for c in combos]
        scored.sort(key=lambda x: x[0], reverse=True)
        best_heuristic_combo = scored[0][1] if scored else []

        # If MC disabled, return heuristic best
        if not self.use_mc:
            return list(best_heuristic_combo)

        # STEP 4: Monte Carlo rollouts
        top_candidates = [c for _, c in scored[:self.mc_params['top_k']]]
        # Silence engine logs
        modules = ['game', 'display', 'turn', 'winconditions', 'cards']
        for m in modules:
            logger.disable(m)

        if self.show_progress:
            print(f"MC Simulation: {len(top_candidates)} candidates × {self.mc_params['rollouts']} rollouts")
        best_combo = best_heuristic_combo
        best_rate = -1.0
        for idx, combo in enumerate(top_candidates, start=1):
            wins = 0
            if self.show_progress:
                print(f" Candidate {idx}/{len(top_candidates)}: ", end="", flush=True)
            for _ in range(self.mc_params['rollouts']):
                sim_game = copy.deepcopy(self.game)
                sim_player = sim_game.players[self.player_id]
                for card, loc in combo:
                    sim_card = next(c for c in sim_player.hand
                                    if c.name == card.name and c.energy_cost == card.energy_cost)
                    sim_game.turn.play_card(sim_card, self.player_id, loc)
                sim_game.play_game_remaining()
                winner = WinConditions(sim_game.locations, sim_game.players).determine_winner()
                if winner == self.player_id:
                    wins += 1
                if self.show_progress:
                    print('.', end='', flush=True)
            rate = wins / self.mc_params['rollouts']
            if self.show_progress:
                print(f" -> {rate:.2f}")
            if rate > best_rate:
                best_rate, best_combo = rate, combo

        # Restore logs
        for m in modules:
            logger.enable(m)

        return list(best_combo)

    def evaluate_sequence(self, combo):
        my_id = self.player_id
        opp_id = 1 - my_id
        cur_my = {loc.position: loc.calculate_total_power(my_id) for loc in self.game.locations}
        cur_opp = {loc.position: loc.calculate_total_power(opp_id) for loc in self.game.locations}
        sim_my = dict(cur_my)
        for card, loc in combo:
            sim_my[loc] = sim_my.get(loc, 0) + card.power
        diff = sum(sim_my.values()) - sum(cur_opp.values())
        score = self.heuristic_weights['power_diff'] * diff
        for card, loc in combo:
            location = self.game.locations[loc]
            if 'Xandar' in location.name:
                score += self.heuristic_weights['xandar_bonus']
            if location.no_destroy:
                score += self.heuristic_weights['no_destroy_bonus']
        return score

    # Deck & hand helpers
    def draw_starting_deck(self, all_cards):
        deck = random.sample(all_cards, 12)
        for c in deck:
            c.owner_id = self.player_id
        return deck

    def draw_starting_hand(self, deck):
        qs = next((c for c in deck if c.name == 'Quicksilver'), None)
        if qs:
            deck.remove(qs)
            hand = random.sample(deck, 3)
            for c in hand:
                deck.remove(c)
            hand.append(qs)
        else:
            hand = random.sample(deck, 4)
            for c in hand:
                deck.remove(c)
        return hand

    def draw_card(self):
        if not self.deck:
            return
        new = random.choice(self.deck)
        if len(self.hand) < 7:
            self.hand.append(new)
            self.deck.remove(new)
