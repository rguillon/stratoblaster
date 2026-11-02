# Copyright (c) 2026 Renaud Guillon
"""The blocks of stone of the cliff faces (GFX-PROP-19, WLD-1-31).

Low-poly chunks of rock, about one unit wide, high and deep, standing on Y = 0 and centred,
stretched to each block's size when placed (`core/scenery/cliff_blocks.py`). Each is a rough
chunk (`render/geometry/rocks.py`): an irregular prism whose corners are pushed about, leaning
sides, a tilted top, every facet its own shade and darker towards its base: a block of fractured
stone, not a box. Three shapes, each a big chunk with smaller ones against it or on it, in grey
crag for the green land and in red mesa rock for the desert.
"""

import math

from game.config.cliffs import CRAG_BLOCK_IDS, MESA_BLOCK_IDS
from render.geometry.rocks import rough_chunk
from render.geometry.rough import Roughness
from render.geometry.solids import Placement, SolidBuilder
from render.scenery.scenery_look import PropGeometry

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

Rgb = list[float]
# __pragma__ ("noskip")

# Grey crag, the same darker, and red mesa rock, the same darker.
CRAG = [0.58, 0.58, 0.55]
CRAG_DARK = [0.5, 0.5, 0.48]
MESA = [0.7, 0.42, 0.28]
MESA_DARK = [0.6, 0.35, 0.23]

# How rough a chunk is: corners pushed in and out by this share of the radius, facets shaded up
# to this much lighter or darker, and this much darker at the base than at the top.
PUSH = 0.2
SHADE = 0.1
SHADOW = 0.12
# The corners round a big chunk and round a smaller stone.
SIDES = 6
SMALL_SIDES = 5


def stone(
    s: SolidBuilder, at: list[float], size: list[float], sides: int, color: Rgb, seed: int
) -> None:
    """Add a chunk of `size` (width, height, depth) at `at`, turned by its seed."""
    yaw = seed * 0.7 * math.pi
    rough_chunk(s, size, sides, color, Roughness(PUSH, SHADE, SHADOW, seed), Placement(at, yaw))


def boulder_block(color: Rgb, seed: int) -> PropGeometry:
    """Return one big chunk, a stone at its foot on its front right."""
    s = SolidBuilder()
    stone(s, [0, 0, 0], [1, 1, 0.95], SIDES, color, seed)
    stone(s, [0.34, 0, 0.3], [0.5, 0.45, 0.5], SMALL_SIDES, color, seed + 1)
    return PropGeometry(s.geometry)


def stacked_block(color: Rgb, seed: int) -> PropGeometry:
    """Return a wide low chunk with a smaller one sitting on it, set back: two courses."""
    s = SolidBuilder()
    stone(s, [0, 0, 0], [1, 0.58, 1], SIDES, color, seed)
    stone(s, [-0.05, 0.5, -0.1], [0.76, 0.5, 0.72], SIDES, color, seed + 1)
    return PropGeometry(s.geometry)


def twin_block(color: Rgb, seed: int) -> PropGeometry:
    """Return two chunks side by side, the right one lower."""
    s = SolidBuilder()
    stone(s, [-0.22, 0, -0.04], [0.66, 1, 0.92], SIDES, color, seed)
    stone(s, [0.28, 0, 0.08], [0.56, 0.74, 0.84], SIDES, color, seed + 1)
    return PropGeometry(s.geometry)


def block_models(ids: list[str], color: Rgb, dark: Rgb, seed: int) -> Any:
    """Return the three block models under `ids`, the second one in the darker stone."""
    return {
        ids[0]: lambda: boulder_block(color, seed),
        ids[1]: lambda: stacked_block(dark, seed + 10),
        ids[2]: lambda: twin_block(color, seed + 20),
    }


CRAG_MODELS = block_models(CRAG_BLOCK_IDS, CRAG, CRAG_DARK, 3)
MESA_MODELS = block_models(MESA_BLOCK_IDS, MESA, MESA_DARK, 40)
