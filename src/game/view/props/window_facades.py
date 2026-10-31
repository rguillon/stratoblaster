"""The windows of a building (D-210): one quad per wall, just off it, mapped on a block of the
windows' atlas (`game/config/window_look.py`) picked at random, so no two walls look the same.
They replace the lit bands and panels of Phase 15 (P15-R09: each face lit differently). D-215: so
do the windows of one wall (a glass front) and the doors, one quad each, for every building."""

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
from render.scenery.window_atlas import atlas_cells, door_column, style_columns  # noqa: E402

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
    style: int | None = None,
) -> None:
    """The windows of a `w` × `d` box at (x, z) (`lot`: `[x, z, w, d]`), from `y0` to `y1`
    (`span`), tinted by `color` (see `tint_of`): one style for the whole box (`style`, or one at
    random), or with `mixed` one per wall (P15-R09: the asymmetric buildings, lit differently on
    each side)."""
    x = lot[0]
    z = lot[1]
    w = lot[2]
    d = lot[3]
    y0 = span[0]
    y1 = span[1]
    if y1 - y0 < MIN_WALL:
        return
    styles = len(WINDOW_ATLAS.styles)
    if style is None:
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


def round_windows(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    windows: QuadBuilder,
    random: Any,  # noqa: ANN401 (a seeded generator)
    tower: list[float],
    span: list[float],
    color: Rgb,
) -> None:
    """The windows of a round tower (`SolidBuilder.cylinder`, maybe tapered): one quad per facet,
    just off it, from `y0` to `y1` (`span`), one style for the whole tower, tinted by `color`.
    `tower` is `[x, z, base, height, radius, top_radius, sides]`: where it stands, the height of
    its foot and how tall it is, its radius at the foot and at the top, and its facets."""
    x = tower[0]
    z = tower[1]
    base = tower[2]
    height = tower[3]
    sides = math.floor(tower[6])
    y0 = span[0]
    y1 = span[1]
    if y1 - y0 < MIN_WALL or height <= 0:
        return

    def radius_at(y: float) -> float:
        return tower[4] + (tower[5] - tower[4]) * (y - base) / height + WINDOW_OFFSET

    style = math.floor(random() * len(WINDOW_ATLAS.styles))
    tint = tint_of(color)
    low = radius_at(y0)
    high = radius_at(y1)
    facet = 2 * (low + high) / 2 * math.sin(math.pi / sides)
    for i in range(sides):
        # The facets' corners are those of `SolidBuilder.lathe`, at i / sides of a turn.
        a = (i / sides) * math.pi * 2
        b = ((i + 1) / sides) * math.pi * 2
        windows.quad(
            [
                [x + low * math.cos(a), y0, z + low * math.sin(a)],
                [x + high * math.cos(a), y1, z + high * math.sin(a)],
                [x + high * math.cos(b), y1, z + high * math.sin(b)],
                [x + low * math.cos(b), y0, z + low * math.sin(b)],
            ],
            wall_uv(random, style, facet, y1 - y0),
            tint,
        )


def _front(face: list[float], width: float) -> list[float]:
    """The ends `[xa, za, xb, zb]` of a quad `width` wide just off a wall facing -Z or +Z (`face`:
    `[x, z, facing]`, the middle of the wall's foot and -1 or 1), in counter-clockwise order seen
    from outside."""
    x = face[0]
    facing = -1 if face[2] < 0 else 1
    z = face[1] + facing * WINDOW_OFFSET
    if facing < 0:
        return [x - width / 2, z, x + width / 2, z]
    return [x + width / 2, z, x - width / 2, z]


def _quad(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    windows: QuadBuilder,
    ends: list[float],
    span: list[float],
    uv: list[float],
    tint: Rgb,
) -> None:
    windows.quad(
        [
            [ends[0], span[0], ends[1]],
            [ends[0], span[1], ends[1]],
            [ends[2], span[1], ends[3]],
            [ends[2], span[0], ends[3]],
        ],
        uv,
        tint,
    )


def wall_windows(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    windows: QuadBuilder,
    random: Any,  # noqa: ANN401 (a seeded generator)
    face: list[float],
    size: list[float],
    style: int,
    color: Rgb,
) -> None:
    """The windows of one wall facing -Z or +Z (D-215: a glass front, a hut's window), one quad of
    `style` just off it: `face` is `[x, z, facing]` (the middle of the wall's foot, -1 or 1), `size`
    is `[width, y0, y1]`, tinted by `color`."""
    width = size[0]
    if width < MIN_WALL or size[2] - size[1] < MIN_WALL:
        return
    uv = wall_uv(random, style, width, size[2] - size[1])
    _quad(windows, _front(face, width), [size[1], size[2]], uv, tint_of(color))


def doorway(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    windows: QuadBuilder,
    random: Any,  # noqa: ANN401 (a seeded generator)
    at: list[float],
    facing: float,
    door: int,
    color: Rgb,
) -> None:
    """A door of style `door` (`DOOR_STYLES`) on a wall facing -Z or +Z (`facing`, -1 or 1), its
    foot's middle at `at` (`[x, y, z]`), tinted by `color` (D-215): one quad of one atlas cell, a
    window cell's size, the door standing on its bottom, lit or not as the atlas has it."""
    cells = atlas_cells(WINDOW_ATLAS)
    col = door_column(WINDOW_ATLAS, door) + math.floor(random() * WINDOW_ATLAS.doorColumns)
    row = math.floor(random() * cells)
    uv = [col / cells, row / cells, (col + 1) / cells, (row + 1) / cells]
    ends = _front([at[0], at[2], facing], WINDOW_CELL.width)
    _quad(windows, ends, [at[1], at[1] + WINDOW_CELL.height], uv, tint_of(color))
