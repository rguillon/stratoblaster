# Copyright (c) 2026 Renaud Guillon
"""Blocks of stone on the steep ground: the cliff faces built of props (GFX-PROP-19).

Where the ground drawn is steeper than a level's `cliffs` rules say, a block of stone stands in
each cell of a grid, sunk into the slope, its front turned downhill, so a face is a stair of chunky
blocks and not a smooth slope. Hashes of the cell decide each block: the same whatever order the
terrain chunks are built in.
"""

import math

from config.scenery_stage import SCENERY_STAGE_CONFIG
from core.math.noise import hash_2d
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
# A block's width, as a share of the spacing (the blocks nearly touch, some overlap).
BLOCK_WIDTH = [0.85, 1.35]


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def cliff_blocks(
    field: HeightField, rules: CliffRules, seed: int, area: GroundArea
) -> list[PropPlacement]:
    """Return the blocks of stone of the cells whose corner lies in `area`.

    One per cell of `rules.spacing` whose ground is steeper than `rules.min_slope`: sunk `embed`
    into the ground drawn (read as the terrain mesh draws it, GFX-PROP-13), turned to face
    downhill, of a kind and a size drawn from the cell's hash. Areas side by side get each block
    once.
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
            gx = (ground.height(x + half, z) - ground.height(x - half, z)) / spacing
            gz = (ground.height(x, z + half) - ground.height(x, z - half)) / spacing
            if math.hypot(gx, gz) < rules.min_slope:
                continue
            kind = kinds[min(len(kinds) - 1, math.floor(hash_2d(i, j, base + 2) * len(kinds)))]
            width = spacing * _lerp(BLOCK_WIDTH[0], BLOCK_WIDTH[1], hash_2d(i, j, base + 3))
            height = _lerp(rules.height[0], rules.height[1], hash_2d(i, j, base + 4))
            depth = _lerp(rules.depth[0], rules.depth[1], hash_2d(i, j, base + 5))
            # The model's front (+Z) turned downhill.
            yaw = math.atan2(-gx, -gz)
            y = ground.height(x, z) - rules.embed
            out.append(PropPlacement(kind, x, y, z, yaw, 1, [width, height, depth]))
    return out
