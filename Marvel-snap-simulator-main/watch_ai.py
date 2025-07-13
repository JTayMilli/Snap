from loguru import logger
logger.remove()            # <-- disable all existing handlers
# (don’t add any new ones, so no debug/info will print)

import sys
from game import Game
from turn import Turn
from winconditions import WinConditions
from enums import Winner

# Simple ASCII UI width settings
BOX_WIDTH = 20  # inner width for each location

# Record structured play events
events = []

# Monkey-patch Turn.play_card to record play events
_orig_play_card = Turn.play_card

def _play_card_record(self, card, player_id, location_id):
    # Call original behavior
    _orig_play_card(self, card, player_id, location_id)
    # Record event: store turn, player, card object, and location
    events.append((self.turn_id, player_id, card, location_id))

Turn.play_card = _play_card_record


def clear_screen():
    # ANSI escape to clear terminal
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()


def render_board(board, last_event):
    turn, player, card, loc = last_event
    clear_screen()
    # Header with play detail
    print(f"Turn {turn+1}: Player {player+1} played {card.name} (Power {card.power}) at Location {loc+1}")
    print(f"Event {events.index(last_event)+1}/{len(events)}\n")

    # Display each location with description and box
    for idx in range(3):
        loc_obj = GAME.locations[idx]
        print(f"Location {idx+1}: {loc_obj.name} — {loc_obj.effect_description}")
        slots_p1 = [f"{c.name[:2]}{c.power}" for c in board[idx][0]]
        slots_p2 = [f"{c.name[:2]}{c.power}" for c in board[idx][1]]
        slots_p1 += ['   '] * (4 - len(slots_p1))
        slots_p2 += ['   '] * (4 - len(slots_p2))
        row1 = ' '.join(f"[{s.center(3)}]" for s in slots_p1)
        row2 = ' '.join(f"[{s.center(3)}]" for s in slots_p2)
        print(f" P1 {row1}")
        print(f" P2 {row2}")
        sum_p1 = sum(c.power for c in board[idx][0])
        sum_p2 = sum(c.power for c in board[idx][1])
        print(f"    Total Power -> P1: {sum_p1}, P2: {sum_p2}")
        if board[idx][0]:
            print("    P1 cards:", ', '.join(f"{c.name}({c.power})" for c in board[idx][0]))
        if board[idx][1]:
            print("    P2 cards:", ', '.join(f"{c.name}({c.power})" for c in board[idx][1]))
        print()

    # Show current hands below the board
    print("Player 1 hand:", ', '.join(f"{c.name}({c.power})" for c in GAME.players[0].hand))
    print("Player 2 hand:", ', '.join(f"{c.name}({c.power})" for c in GAME.players[1].hand))

    print("\n(Press Enter to advance)")


def main():
    global GAME
    GAME = Game()
    GAME.play_game()

    # Build initial empty board state
    board = {i: {0: [], 1: []} for i in range(3)}

    # Replay events in sequence
    for evt in events:
        turn, player, card, loc = evt
        board[loc][player].append(card)
        render_board(board, evt)
        input()

    # After replay, display the game winner
    clear_screen()
    winner_val = WinConditions(GAME.locations, GAME.players).determine_winner()
    if winner_val == Winner.PLAYER1.value:
        print("Player 1 wins the game!")
    elif winner_val == Winner.PLAYER2.value:
        print("Player 2 wins the game!")
    else:
        print("The game is a draw!")

    # Display final hands below winner announcement
    print("\nFinal hands:")
    print("Player 1:", ', '.join(f"{c.name}({c.power})" for c in GAME.players[0].hand))
    print("Player 2:", ', '.join(f"{c.name}({c.power})" for c in GAME.players[1].hand))

if __name__ == '__main__':
    main()
