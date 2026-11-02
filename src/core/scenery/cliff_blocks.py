# Copyright (c) 2026 Renaud Guillon
"""Blocks of stone on the steep ground: the cliff faces built of props (GFX-PROP-19).

Where the ground drawn is steeper than a level's `cliffs` rules say, a block of stone stands in
each cell of a grid, sunk into the slope, its front turned downhill, so a face is a stair of chunky
blocks and not a smooth slope. Hashes of the cell decide each block: the same whatever order the
terrain chunks are built in.
"""

import math

from config.scenery_stage import SCENERY_STAGE_CONFIG
from core.math.noise import hash_2d, smoothstep
from core.scenery.ground_boxes import PropPlacement
from core.scenery.ground_fit import SampledGround

# isort: split
# __pragma__ ("skip")
from core.scenery.ground_boxes import GroundArea
from core.scenery.height_field import HeightField
from core.scenery.scenery_level import CliffRules

# __pragma__ ("noskip")


# The hash draw of the blocks (apart from the buildings' and the trees', `prop_placement`).
DRAW_CLIFFS = 11
# A block stands between these shares of its cell from the cell's corner.
BLOCK_JITTER = [0.2, 0.8]
# A block's width, as a share of the spacing (the blocks touch, many overlap).
BLOCK_WIDTH = [1.0, 2.0]
# A block's bulk is the square of its draw, so most blocks are modest and a few are big; each
# size is half the bulk and half its own draw.
BULK_POWER = 2
# Blocks start, at this share of the slope threshold, as a fringe of scattered stones between the
# grass and the face: only this share of the cells, scaled down by this much, growing to full
# size at the threshold.
FRINGE = 0.7
FRINGE_CHANCE = 0.5
FRINGE_SCALE = 0.45
# A block is sunk further by this share of its depth times the slope, so its downhill edge meets
# the ground instead of hanging over it.
SINK = 0.4


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _size(bulk: float, i: int, j: int, seed: int) -> float:
    """Return the draw of one size of a block: half its bulk, half its own."""
    return (bulk + hash_2d(i, j, seed)) / 2


def cliff_blocks(
    field: HeightField, rules: CliffRules, seed: int, area: GroundArea, min_height: float
) -> list[PropPlacement]:
    """Return the blocks of stone of the cells whose corner lies in `area`.

    One per cell of `rules.spacing` whose ground is steeper than `rules.min_slope` and above
    `min_height` (the props' limit, just above the sea: none on the shelves under it), and a
    fringe of smaller ones in some of the cells a little less steep: sunk `embed` into the ground
    drawn (read as the terrain mesh draws it, GFX-PROP-13) and further into the slope, turned to
    face downhill, of a kind and a size drawn from the cell's hash. Areas side by side get each
    block once.
    """
    spacing = rules.spacing
    i0 = math.ceil(area.x_min / spacing)
    i1 = math.ceil(area.x_max / spacing)
    j0 = math.ceil(area.z_min / spacing)
    j1 = math.ceil(area.z_max / spacing)
    out: list[PropPlacement] = []
    if i1 <= i0 or j1 <= j0 or len(rules.kinds) == 0:
        return out
    # The slope is read half a spacing round each block.
    margin = spacing
    size = max(area.x_max - area.x_min, area.z_max - area.z_min) + 2 * margin
    ground = SampledGround(
        field, area.x_min - margin, area.z_min - margin, size, SCENERY_STAGE_CONFIG.cell
    )
    half = spacing / 2
    base = seed * 31 + DRAW_CLIFFS
    kinds = rules.kinds
    for j in range(j0, j1):
        for i in range(i0, i1):
            x = (i + _lerp(BLOCK_JITTER[0], BLOCK_JITTER[1], hash_2d(i, j, base))) * spacing
            z = (j + _lerp(BLOCK_JITTER[0], BLOCK_JITTER[1], hash_2d(i, j, base + 1))) * spacing
            top = ground.height(x, z)
            if top < min_height:
                continue
            gx = (ground.height(x + half, z) - ground.height(x - half, z)) / spacing
            gz = (ground.height(x, z + half) - ground.height(x, z - half)) / spacing
            slope = math.hypot(gx, gz)
            if slope < rules.min_slope * FRINGE:
                continue
            if slope < rules.min_slope and hash_2d(i, j, base + 6) >= FRINGE_CHANCE:
                continue
            scale = _lerp(
                FRINGE_SCALE, 1, smoothstep(rules.min_slope * FRINGE, rules.min_slope, slope)
            )
            kind = kinds[min(len(kinds) - 1, math.floor(hash_2d(i, j, base + 2) * len(kinds)))]
            bulk = math.pow(hash_2d(i, j, base + 7), BULK_POWER)
            width = (
                scale * spacing * _lerp(BLOCK_WIDTH[0], BLOCK_WIDTH[1], _size(bulk, i, j, base + 3))
            )
            height = scale * _lerp(rules.height[0], rules.height[1], _size(bulk, i, j, base + 4))
            depth = scale * _lerp(rules.depth[0], rules.depth[1], _size(bulk, i, j, base + 5))
            # The model's front (+Z) turned downhill.
            yaw = math.atan2(-gx, -gz)
            y = top - rules.embed - SINK * depth * slope
            out.append(PropPlacement(kind, x, y, z, yaw, 1, [width, height, depth]))
    return out
