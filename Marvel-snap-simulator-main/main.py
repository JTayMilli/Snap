import argparse
import os
import sys
from loguru import logger

# Add the project root to the Python path to allow imports from any file
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import Game
from visualizer import SnapVisualizer

def main():
    """
    Main function to run the simulator or the visualizer.
    """
    log_file = "game_log.txt"

    parser = argparse.ArgumentParser(description="Marvel Snap Simulator")
    parser.add_argument("--visualize", action="store_true",
                        help="Visualize the last simulated game from game_log.txt.")
    args = parser.parse_args()

    if args.visualize:
        if not os.path.exists(log_file):
            print(f"Error: Log file '{log_file}' not found. Run a simulation first.")
            return
        logger.info(f"Visualizing game from {log_file}")
        SnapVisualizer(log_file).run()
    else:
        # --- Simulation Mode ---
        # Automatically delete the previous game log
        if os.path.exists(log_file):
            os.remove(log_file)
        
        # Configure logger to write to the new log file.
        # The format is designed to be easily parsed by the visualizer.
        logger.add(log_file, format="{message}", level="INFO", backtrace=False, diagnose=False)
        
        logger.info("Starting new game simulation...")
        
        # Define decks for the players
        player1_deck = ["Sunspot", "Ant-Man", "Nightcrawler", "Iron Fist", "Wolfsbane", "Mister Sinister", "Kraven", "Multiple Man", "Vulture", "Doctor Strange", "Heimdall", "Hulk"]
        player2_deck = ["Sunspot", "Ant-Man", "Nightcrawler", "Iron Fist", "Wolfsbane", "Mister Sinister", "Kraven", "Multiple Man", "Vulture", "Doctor Strange", "Heimdall", "Hulk"]
        
        # Create and run the game
        game = Game(player1_deck, player2_deck)
        game.play()
        logger.info("Simulation finished. Run with --visualize to see the replay.")

if __name__ == "__main__":
    main()
