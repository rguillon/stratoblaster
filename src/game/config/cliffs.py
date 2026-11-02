# Copyright (c) 2026 Renaud Guillon
"""The blocks of stone of the cliff faces (GFX-PROP-19, WLD-1-31).

Three shapes of block each, in grey crag for the green land and in red mesa rock for the desert
(`src/game/view/props/crag_props.py` draws them). The rules say where they stand: on ground steeper
than `minSlope` (height per unit; the hills' faces, the walls of the mesas, buttes and canyon), one
in each cell of `spacing`, `height` and `depth` drawn from their ranges, sunk `embed` into the
ground.
"""

from game.config.record import record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")

CRAG_BLOCK_IDS = ["crag-block-a", "crag-block-b", "crag-block-c"]
MESA_BLOCK_IDS = ["mesa-block-a", "mesa-block-b", "mesa-block-c"]


def cliffs(kinds: list[str]) -> Any:
    """Return the cliff rules of World 1 with the blocks of `kinds`."""
    return record({
        "kinds": kinds,
        "minSlope": 0.55,
        "spacing": 7,
        "height": [7, 12],
        "depth": [5, 9],
        "embed": 2.5,
    })


CRAG_CLIFFS = cliffs(CRAG_BLOCK_IDS)
MESA_CLIFFS = cliffs(MESA_BLOCK_IDS)
