from loguru import logger

def display_board(game):
    """
    Displays the current board state to the console and logs it in a
    machine-readable format for the visualizer.
    """
    logger.info(f"--- Turn {game.turn} ---")
    
    # Log machine-readable data for the visualizer
    logger.info(f"VIZ_TURN:{game.turn}")
    p1_hand = ", ".join([card.name for card in game.player1.hand])
    p2_hand = ", ".join([card.name for card in game.player2.hand])
    logger.info(f"VIZ_P1_HAND:{p1_hand if p1_hand else 'Empty'}")
    logger.info(f"VIZ_P2_HAND:{p2_hand if p2_hand else 'Empty'}")
    logger.info(f"VIZ_P1_ENERGY:{game.player1.energy}/{game.turn}")
    logger.info(f"VIZ_P2_ENERGY:{game.player2.energy}/{game.turn}")

    # Prepare data for visual display
    locations_data = []
    for i, location in enumerate(game.locations):
        p1_power = location.get_power(game.player1.player_id)
        p2_power = location.get_power(game.player2.player_id)
        
        # Log location data for visualizer
        logger.info(f"VIZ_LOCATION:{i}:{location.name}:{p1_power}:{p2_power}")

        p1_cards = location.get_cards(player=game.player1.player_id)
        p2_cards = location.get_cards(player=game.player2.player_id)
        
        for card in p1_cards:
            logger.info(f"VIZ_CARD:{i}:1:{card.name}:{card.power}")
        for card in p2_cards:
            logger.info(f"VIZ_CARD:{i}:2:{card.name}:{card.power}")

        locations_data.append({
            "name": location.name,
            "p1_power": p1_power,
            "p2_power": p2_power,
            "p1_cards": [f"{c.name} ({c.power})" for c in p1_cards],
            "p2_cards": [f"{c.name} ({c.power})" for c in p2_cards]
        })

    # Print human-readable board to console
    console_output = "\n"
    console_output += "+-------------------------+-------------------------+-------------------------+\n"
    console_output += f"| {locations_data[0]['name']:<23} | {locations_data[1]['name']:<23} | {locations_data[2]['name']:<23} |\n"
    console_output += f"| P1: {locations_data[0]['p1_power']:<2} | P2: {locations_data[0]['p2_power']:<2}      | P1: {locations_data[1]['p1_power']:<2} | P2: {locations_data[1]['p2_power']:<2}      | P1: {locations_data[2]['p1_power']:<2} | P2: {locations_data[2]['p2_power']:<2}      |\n"
    console_output += "+-------------------------+-------------------------+-------------------------+\n"
    
    max_cards = max(len(loc['p1_cards']) for loc in locations_data) + max(len(loc['p2_cards']) for loc in locations_data)
    max_cards = max(4, max_cards) # show at least 4 slots

    for i in range(max_cards):
        row_str = "|"
        for loc in locations_data:
            card_str = loc['p2_cards'][i] if i < len(loc['p2_cards']) else ""
            row_str += f" {card_str:<23} |"
        console_output += row_str + "\n"

    console_output += "+-------------------------+-------------------------+-------------------------+\n"

    for i in range(max_cards):
        row_str = "|"
        for loc in locations_data:
            card_str = loc['p1_cards'][i] if i < len(loc['p1_cards']) else ""
            row_str += f" {card_str:<23} |"
        console_output += row_str + "\n"

    console_output += "+-------------------------+-------------------------+-------------------------+\n"
    logger.info(console_output)
