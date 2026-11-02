# Copyright (c) 2026 Renaud Guillon
"""Player ship models, keyed by the ids of `PLAYER_SHIPS`, each built in code (GFX-ART-01)."""

from game.view.balanced_ship import build_balanced_ship
from game.view.heavy_ship import build_heavy_ship
from game.view.light_ship import build_light_ship

PLAYER_SHIP_MODELS = {
    "balanced": build_balanced_ship,
    "heavy": build_heavy_ship,
    "light": build_light_ship,
}
