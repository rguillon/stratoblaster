# Copyright (c) 2026 Renaud Guillon
"""The blocks of stone of the cliff faces (GFX-PROP-19, WLD-1-31).

Low-poly chunks of rock, one unit wide, high and deep, standing on Y = 0 and centred, scaled to
each block's size when placed (`core/scenery/cliff_blocks.py`). Three shapes: a plain block, a
block whose top is chipped back, and a block with a ledge: in grey crag for the green land and in
red mesa rock for the desert.
"""

from game.config.cliffs import CRAG_BLOCK_IDS, MESA_BLOCK_IDS
from render.geometry.solids import Placement, SolidBuilder
from render.scenery.scenery_look import PropGeometry

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")

# Grey crag (the sides, darker, and the tops, lit) and red mesa rock.
CRAG = [[0.56, 0.57, 0.55], [0.7, 0.7, 0.68]]
CRAG_DARK = [[0.48, 0.49, 0.48], [0.62, 0.62, 0.6]]
MESA = [[0.68, 0.38, 0.24], [0.8, 0.5, 0.33]]
MESA_DARK = [[0.58, 0.31, 0.19], [0.7, 0.42, 0.27]]


def _box(s: SolidBuilder, size: list[float], at: list[float], colors: list[list[float]]) -> None:
    s.box(size, colors[0], Placement(at), colors[1])


def plain_block(colors: list[list[float]]) -> PropGeometry:
    """Return a plain block, a little wider at its base."""
    s = SolidBuilder()
    _box(s, [1, 0.35, 1], [0, 0, 0], colors)
    _box(s, [0.94, 0.65, 0.92], [0, 0.35, 0.02], colors)
    return PropGeometry(s.geometry)


def chipped_block(colors: list[list[float]]) -> PropGeometry:
    """Return a block whose top front corner is chipped back: a weathered lip."""
    s = SolidBuilder()
    _box(s, [1, 0.6, 1], [0, 0, 0], colors)
    _box(s, [0.96, 0.4, 0.7], [0, 0.6, -0.15], colors)
    return PropGeometry(s.geometry)


def ledge_block(colors: list[list[float]]) -> PropGeometry:
    """Return a block with a ledge: its upper half set back, a step on its front."""
    s = SolidBuilder()
    _box(s, [1, 0.5, 1], [0, 0, 0], colors)
    _box(s, [0.8, 0.5, 0.55], [0.05, 0.5, -0.22], colors)
    return PropGeometry(s.geometry)


def block_models(ids: list[str], colors: list[list[float]], dark: list[list[float]]) -> Any:
    """Return the three block models under `ids`, the second one in the darker stone."""
    return {
        ids[0]: lambda: plain_block(colors),
        ids[1]: lambda: chipped_block(dark),
        ids[2]: lambda: ledge_block(colors),
    }


CRAG_MODELS = block_models(CRAG_BLOCK_IDS, CRAG, CRAG_DARK)
MESA_MODELS = block_models(MESA_BLOCK_IDS, MESA, MESA_DARK)
