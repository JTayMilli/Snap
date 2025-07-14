# marvel_snap_rl/card_data.py

from dataclasses import dataclass
from typing import Dict, Optional

@dataclass(frozen=True)
class CardDefinition:
    """
    Represents the static definition of a card.
    'frozen=True' makes instances of this class immutable.
    """
    name: str
    cost: int
    power: int
    ability: Optional[str] = None

# A central dictionary containing all card definitions in the game.
# The key is the card_id (a unique string), and the value is the CardDefinition.
# This makes it easy to look up card properties.
CARD_DEFINITIONS: Dict[str, CardDefinition] = {
    # --- No Ability Cards ---
    "abomination": CardDefinition(name="Abomination", cost=5, power=9),
    "cyclops": CardDefinition(name="Cyclops", cost=3, power=4),
    "hulk": CardDefinition(name="Hulk", cost=6, power=12),
    "misty_knight": CardDefinition(name="Misty Knight", cost=1, power=2),
    "shocker": CardDefinition(name="Shocker", cost=2, power=3),
    "the_thing": CardDefinition(name="The Thing", cost=4, power=6),
    "wasp": CardDefinition(name="Wasp", cost=0, power=1),

    # --- On Reveal Cards ---
    "carnage": CardDefinition(
        name="Carnage",
        cost=2,
        power=2,
        ability="On Reveal: Destroy your other cards here. +2 Power for each card destroyed."
    ),
    "hawkeye": CardDefinition(
        name="Hawkeye",
        cost=1,
        power=1,
        ability="On Reveal: If you play a card here next turn, +2 Power."
    ),
    "medusa": CardDefinition(
        name="Medusa",
        cost=2,
        power=2,
        ability="On Reveal: If this is at the middle location, +2 Power."
    ),
    "sentinel": CardDefinition(
        name="Sentinel",
        cost=2,
        power=3,
        ability="On Reveal: Add another Sentinel to your hand."
    ),
    "star_lord": CardDefinition(
        name="Star-Lord",
        cost=2,
        power=2,
        ability="On Reveal: If your opponent played a card here this turn, +3 Power."
    ),
    "white_queen": CardDefinition(
        name="White Queen",
        cost=4,
        power=6,
        ability="On Reveal: Draw a copy of the highest Cost card in your opponent's hand."
    ),

    # --- Ongoing Cards ---
    "ant_man": CardDefinition(
        name="Ant-Man",
        cost=1,
        power=1,
        ability="Ongoing: If you have 3 other cards here, +3 Power."
    ),
    "captain_america": CardDefinition(
        name="Captain America",
        cost=3,
        power=3,
        ability="Ongoing: Your other cards at this location have +1 Power."
    ),
    "iron_man": CardDefinition(
        name="Iron Man",
        cost=5,
        power=0,
        ability="Ongoing: Your total Power is doubled at this Location."
    ),
    "klaw": CardDefinition(
        name="Klaw",
        cost=5,
        power=4,
        ability="Ongoing: The location to the right has +6 Power."
    ),
    "mr_fantastic": CardDefinition(
        name="Mr. Fantastic",
        cost=3,
        power=2,
        ability="Ongoing: Adjacent locations have +2 Power."
    ),
}

if __name__ == '__main__':
    # Example of how to access card data
    iron_man_def = CARD_DEFINITIONS["iron_man"]
    print(f"Card: {iron_man_def.name}")
    print(f"Cost: {iron_man_def.cost}")
    print(f"Power: {iron_man_def.power}")
    print(f"Ability: {iron_man_def.ability}")

    cyclops_def = CARD_DEFINITIONS["cyclops"]
    print(f"\nCard: {cyclops_def.name}")
    print(f"Cost: {cyclops_def.cost}")
    print(f"Power: {cyclops_def.power}")
    print(f"Ability: {cyclops_def.ability}")
