"""The `props/` page on the grid of tiles (phase 15), ported from `app/prop-viewer-layout.ts`: each
prop on whole tiles, in a cell of the layout, and with streets, the cells ringed by one-tile roads,
so the buildings stand in blocks."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from core.scenery.road_tiles import PieceSide, RoadPiece  # noqa: E402

# Steps to the neighbour beyond each side (+Z, +X, -Z, -X).
_STEPS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


class TileLayout:
    """Where the props and the roads go, in tiles.

    `centres`: centre of each prop, in tiles (a half tile for an odd footprint). `roads`: the road
    pieces. `bounds`: the tiles the layout covers, as [x0, x1, z0, z1].
    """

    def __init__(self, centres: list[Any], roads: list[RoadPiece], bounds: list[Any]) -> None:
        self.centres = centres
        self.roads = roads
        self.bounds = bounds


def _max_of(values: list[float]) -> float:
    """`Math.max(...values)`: -Infinity for no values."""
    best = float("-Infinity")
    for value in values:
        best = max(best, value)
    return best


# Open sides of a one-tile piece that make it a tee, a cross, or a turn (two sides, not straight).
_TEE = 3
_CROSS = 4
_TURN_SIDES = 2


def _road_pieces(roads: dict[str, bool], tiles: list[Any]) -> list[RoadPiece]:
    """The one-tile road pieces on the tiles of `roads`, each open toward its road neighbours."""
    side = PieceSide(1, 0)
    pieces: list[RoadPiece] = []
    for x, z in tiles:
        opens = [(str(x + dx) + "," + str(z + dz)) in roads for dx, dz in _STEPS]
        count = 0
        for is_open in opens:
            if is_open:
                count += 1
        straight = opens[0] == opens[2] and opens[1] == opens[3]
        if count == _TEE:
            kind = "tee"
        elif count == _CROSS:
            kind = "cross"
        elif count == _TURN_SIDES and not straight:
            kind = "turn"
        else:
            kind = "straight"
        sides: list[PieceSide | None] = [side if is_open else None for is_open in opens]
        pieces.append(RoadPiece(x, z, 1, kind, False, sides))
    return pieces


def _centre(start: float, room: float, w: float) -> float:
    """Where a footprint of `w` tiles starts in a block of `room` tiles from `start`, centred."""
    return start + math.floor((room - w) / 2) + w / 2


def _packed_layout(footprints: list[Any], gap: float) -> TileLayout:
    """Without streets: rows of props side by side, each `gap` tiles from the next, so a large prop
    (the road sample) does not spread the small ones apart."""
    columns = int(max(1, math.ceil(math.sqrt(len(footprints)))))
    rows: list[list[Any]] = []
    for i in range(len(footprints)):
        if i % columns == 0:
            rows.append([])
        rows[len(rows) - 1].append(footprints[i])
    widths: list[float] = []
    depths: list[float] = []
    for row in rows:
        total = gap
        deepest = float("-Infinity")
        for footprint in row:
            total += footprint[0] + gap
            deepest = max(deepest, footprint[1])
        widths.append(total)
        depths.append(deepest)
    width = _max_of(widths)
    depth = gap
    for d in depths:
        depth += d + gap
    ox = -math.floor(width / 2)
    oz = -math.floor(depth / 2)
    centres: list[list[float]] = []
    z = oz + depth - gap
    for r in range(len(rows)):
        row_depth = depths[r] if r < len(depths) else 1
        z -= row_depth
        x = ox + gap
        for w, d in rows[r]:
            centres.append([x + w / 2, _centre(z, row_depth, d)])
            x += w + gap
        z -= gap
    return TileLayout(centres, [], [ox, ox + width, oz, oz + depth])


def tile_layout(footprints: list[Any], gap: float, streets: bool) -> TileLayout:
    """Lays out props whose footprints are `footprints` (in tiles, width x depth) on a square-ish
    grid of cells, `gap` tiles between them; with `streets`, the gaps are roads one tile wide."""
    if not streets:
        return _packed_layout(footprints, gap)
    sizes: list[float] = []
    for footprint in footprints:
        sizes.append(footprint[0])
        sizes.append(footprint[1])
    room = max(1, _max_of(sizes))
    cell = room + gap
    columns = int(max(1, math.ceil(math.sqrt(len(footprints)))))
    rows = int(max(1, math.ceil(len(footprints) / columns)))
    ox = -math.floor((columns * cell + gap) / 2)
    oz = -math.floor((rows * cell + gap) / 2)
    centres: list[list[float]] = []
    for i in range(len(footprints)):
        w = footprints[i][0]
        d = footprints[i][1]
        centres.append(
            [
                _centre(ox + (i % columns) * cell + gap, room, w),
                _centre(oz + (rows - 1 - math.floor(i / columns)) * cell + gap, room, d),
            ]
        )
    bounds = [ox, ox + columns * cell + gap, oz, oz + rows * cell + gap]
    if gap == 0:
        return TileLayout(centres, [], bounds)
    tiles: list[Any] = []
    for x in range(int(bounds[0]), int(bounds[1])):
        for z in range(int(bounds[2]), int(bounds[3])):
            if (x - ox) % cell < gap or (z - oz) % cell < gap:
                tiles.append([x, z])
    road_set: dict[str, bool] = {}
    for x, z in tiles:
        road_set[str(x) + "," + str(z)] = True
    return TileLayout(centres, _road_pieces(road_set, tiles), bounds)
