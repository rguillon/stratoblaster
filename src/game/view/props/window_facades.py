"""The windows of a building (D-210): one quad per wall, just off it, mapped on a block of the
windows' atlas (`game/config/window_look.py`) picked at random, so no two walls look the same.
They replace the lit bands and panels of Phase 15 (P15-R09: each face lit differently)."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from render.geometry.textured import QuadBuilder  # noqa: E402

Rgb = list[float]
__pragma__("noskip")

from game.config.window_look import (  # noqa: E402
    WINDOW_ATLAS,
    WINDOW_CELL,
    WINDOW_OFFSET,
    WINDOW_TINT,
)
from render.scenery.window_atlas import atlas_cells, style_columns  # noqa: E402

# Walls narrower or lower than this get no windows.
MIN_WALL = 1


def tint_of(color: Rgb) -> Rgb:
    """The vertex colour of a building's windows: its window colour, `WINDOW_TINT` of it, over
    white (the atlas has the colours)."""
    k: float = WINDOW_TINT
    return [1 - k + color[0] * k, 1 - k + color[1] * k, 1 - k + color[2] * k]


def wall_uv(random: Any, style: int, length: float, height: float) -> list[float]:  # noqa: ANN401
    """The `[u0, v0, u1, v1]` of a wall `length` × `height` in the band of `style`: one atlas cell
    per `WINDOW_CELL`, the block at a random place in the band (no wider than the band: a longer
    wall gets wider windows)."""
    cells = atlas_cells(WINDOW_ATLAS)
    band = style_columns(WINDOW_ATLAS)
    cols = min(band, max(1, math.floor(length / WINDOW_CELL.width + 0.5)))
    rows = max(1, math.floor(height / WINDOW_CELL.height + 0.5))
    col = style * band + math.floor(random() * (band - cols + 1))
    # Any row: the atlas wraps along V.
    row = math.floor(random() * cells)
    return [col / cells, row / cells, (col + cols) / cells, (row + rows) / cells]


def facade_windows(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    windows: QuadBuilder,
    random: Any,  # noqa: ANN401 (a seeded generator)
    lot: list[float],
    span: list[float],
    color: Rgb,
    mixed: bool = False,  # noqa: FBT001, FBT002
) -> None:
    """The windows of a `w` × `d` box at (x, z) (`lot`: `[x, z, w, d]`), from `y0` to `y1`
    (`span`), tinted by `color` (see `tint_of`): one style for the whole box, or with `mixed` one
    per wall (P15-R09: the asymmetric buildings, lit differently on each side)."""
    x = lot[0]
    z = lot[1]
    w = lot[2]
    d = lot[3]
    y0 = span[0]
    y1 = span[1]
    if y1 - y0 < MIN_WALL:
        return
    styles = len(WINDOW_ATLAS.styles)
    style = math.floor(random() * styles)
    tint = tint_of(color)
    xl = x - w / 2 - WINDOW_OFFSET
    xr = x + w / 2 + WINDOW_OFFSET
    zf = z - d / 2 - WINDOW_OFFSET
    zb = z + d / 2 + WINDOW_OFFSET
    # Each wall's bottom edge, its ends in counter-clockwise order seen from outside, and its
    # length.
    walls = [
        [x - w / 2, zf, x + w / 2, zf, w],
        [xr, z - d / 2, xr, z + d / 2, d],
        [x + w / 2, zb, x - w / 2, zb, w],
        [xl, z + d / 2, xl, z - d / 2, d],
    ]
    for wall in walls:
        if wall[4] < MIN_WALL:
            continue
        if mixed:
            style = math.floor(random() * styles)
        windows.quad(
            [
                [wall[0], y0, wall[1]],
                [wall[0], y1, wall[1]],
                [wall[2], y1, wall[3]],
                [wall[2], y0, wall[3]],
            ],
            wall_uv(random, style, wall[4], y1 - y0),
            tint,
        )
