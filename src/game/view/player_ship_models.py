# Copyright (c) 2026 Renaud Guillon
"""The player ship's model, keyed by its id in `PLAYER_SHIPS`, built in code (GFX-ART-01)."""

from game.view.balanced_ship import build_balanced_ship

PLAYER_SHIP_MODELS = {
    "balanced": build_balanced_ship,
}
