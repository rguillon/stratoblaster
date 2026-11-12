# Copyright (c) 2026 Renaud Guillon
"""The player ship's model, keyed by its id in `PLAYER_SHIPS`, built in code (GFX-ART-01)."""

from game.view.ship_model import build_playfield_ship

# The playfield's builds (D-355): their glowing edges sized for the ship's playfield scale. The
# title backdrop builds the ship at its own, larger size (`build_player_ship`).
PLAYER_SHIP_MODELS = {
    "player": build_playfield_ship,
}
