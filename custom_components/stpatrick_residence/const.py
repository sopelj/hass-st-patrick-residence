"""Constants used for mug."""

from typing import Final

DOMAIN: Final[str] = "stpatrick_residence"
CONFIG_VERSION = 1

BASE_URL = "https://live1.tvtour-network.com/portail"

MEAL_TYPE_MAPPING = {
    "Entrée": "appetizer",
    "Dîner": "lunch",
    "Dessert": "dessert",
    "Souper": "dinner",
}
