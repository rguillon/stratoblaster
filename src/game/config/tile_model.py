# Copyright (c) 2026 Renaud Guillon
"""What a model made for the grid of tiles is.

Phase 15: split out of `tile_buildings.py`. The kinds of models made for the grid are the
archetypes named in the TS `TileArchetype` type; each is built for any W x D tiles (GFX-BLDG-03).
"""

from game.config.record import record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def model(archetype: str, w: int, d: int, seed: int = 1) -> Any:
    """Return a model made for the grid: what it is, its tiles (X x Z, front -Z) and its variant."""
    suffix = "-" + str(seed) if seed > 1 else ""
    return record({
        "id": "tile-" + archetype + "-" + str(w) + "x" + str(d) + suffix,
        "archetype": archetype,
        "tiles": [w, d],
        "seed": seed,
    })
