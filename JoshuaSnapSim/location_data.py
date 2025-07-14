# marvel_snap_rl/location_data.py

from dataclasses import dataclass
from typing import Dict, Optional

@dataclass(frozen=True)
class LocationDefinition:
    """
    Represents the static definition of a location.
    'frozen=True' makes instances of this class immutable.
    """
    name: str
    description: Optional[str] = None

# A central dictionary containing all location definitions in the game.
# The key is the location_id (a unique string), and the value is the LocationDefinition.
LOCATION_DEFINITIONS: Dict[str, LocationDefinition] = {
    # --- Neutral Locations ---
    "new_york": LocationDefinition(
        name="New York",
        description="On turn 6, you can move cards to this location."
    ),
    "ruins": LocationDefinition(
        name="Ruins",
        description=None # No effect
    ),

    # --- Power/Cost Modifying Locations ---
    "asgard": LocationDefinition(
        name="Asgard",
        description="After turn 4, whoever is winning here draws 2 cards."
    ),
    "elysium": LocationDefinition(
        name="Elysium",
        description="Cards cost 1 less."
    ),
    "muir_island": LocationDefinition(
        name="Muir Island",
        description="After each turn, give cards here +1 Power."
    ),
    "nidavellir": LocationDefinition(
        name="Nidavellir",
        description="Cards here have +5 Power."
    ),
    "xandar": LocationDefinition(
        name="Xandar",
        description="Cards here have +1 Power."
    ),

    # --- Card Adding/Removing Locations ---
    "savage_land": LocationDefinition(
        name="Savage Land",
        description="Add a Raptor to each side of this location."
    ),
    "sokovia": LocationDefinition(
        name="Sokovia",
        description="On reveal, discard a card from each player's hand."
    ),
    "wakanda": LocationDefinition(
        name="Wakanda",
        description="Cards here can't be destroyed."
    ),

    # --- Restrictive Locations ---
    "death's_domain": LocationDefinition(
        name="Death's Domain",
        description="When you play a card here, destroy it."
    ),
    "knowhere": LocationDefinition(
        name="Knowhere",
        description="On Reveal effects don't happen at this location."
    ),
    "the_vault": LocationDefinition(
        name="The Vault",
        description="On turn 6, cards can't be played here."
    ),
}

if __name__ == '__main__':
    # Example of how to access location data
    wakanda_def = LOCATION_DEFINITIONS["wakanda"]
    print(f"Location: {wakanda_def.name}")
    print(f"Description: {wakanda_def.description}")

    ruins_def = LOCATION_DEFINITIONS["ruins"]
    print(f"\nLocation: {ruins_def.name}")
    print(f"Description: {ruins_def.description}")
