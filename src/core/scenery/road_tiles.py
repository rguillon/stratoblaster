"""P15-R03, R04: the road pieces of the districts laid on tiles (phase 15), found from their
straight streets: a junction piece where a row and a column meet, the size of the wider road, and
straight pieces of N × N tiles along each road between them. Ported from
`core/scenery/road-tiles.ts`.

Sets of tile keys are dicts keyed by `str(tile_key(x, z))` (see `tile_has`), and a `Map` keyed by
tile key is kept in the order its keys were first set, as the TypeScript `Map` is.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

from core.scenery.road_types import Road  # noqa: E402
from core.scenery.scenery_level import TileRules  # noqa: E402

__pragma__("noskip")

EPSILON = 1e-6
# Open sides of a junction with all four, and with three (a tee).
FULL_SIDES = 4
THREE_SIDES = 3
# Tiles across a level, at most (keys stay unique within it).
ACROSS = 4096


class PieceSide:
    """An open side of a piece: a road `size` tiles wide, `offset` tiles from the low edge."""

    def __init__(self, size: int, offset: int) -> None:
        self.size = size
        self.offset = offset


class RoadPiece:
    """A road piece: `size` × `size` tiles from tile (`x`, `z`), with its open sides."""

    def __init__(
        self,
        x: int,
        z: int,
        size: int,
        kind: str,
        adapter: bool,
        sides: list[PieceSide | None],
    ) -> None:
        self.x = x
        self.z = z
        self.size = size
        self.kind = kind
        """`straight`, `turn`, `tee` or `cross`."""
        self.adapter = adapter
        """Whether roads of two sizes meet in it (P15-R04)."""
        self.sides = sides


class _TileLine:
    """A straight street on the grid: a row (along X) or a column, with its tiles."""

    def __init__(
        self,
        row: bool,
        start: int,
        size: int,
        at: float,
        from_: float,
        to: float,
    ) -> None:
        self.row = row
        self.start = start
        """First tile across it."""
        self.size = size
        """Size in tiles."""
        self.at = at
        """Where its middle is across (world units)."""
        self.from_ = from_
        self.to = to
        """Its ends along (world units)."""


def tile_key(x: int, z: int) -> int:
    """Key of a tile: one number (keys are made a lot while packing blocks)."""
    return z * ACROSS + x + ACROSS // 2


def tile_has(tiles: dict[str, bool], x: int, z: int) -> bool:
    """Whether the tile (`x`, `z`) is in the set `tiles` (see the module doc)."""
    return str(tile_key(x, z)) in tiles


def _line_of(road: Road, tile: TileRules) -> _TileLine | None:
    if len(road.points) == 0:
        return None
    a = road.points[0]
    b = road.points[len(road.points) - 1]
    row = abs(a.z - b.z) < EPSILON
    size = max(1, math.floor(road.width / tile.size + 0.5))
    at = a.z if row else a.x
    p = a.x if row else a.z
    q = b.x if row else b.z
    start = math.floor(at / tile.size - size / 2 + 0.5)
    return _TileLine(row, start, size, at, min(p, q), max(p, q))


def _kind_of(sides: Sequence[PieceSide | None]) -> str:
    """The kind of a piece by its open sides."""
    open_sides = [s is not None for s in sides]
    count = 0
    for o in open_sides:
        if o:
            count += 1
    if count == FULL_SIDES:
        return "cross"
    if count == THREE_SIDES:
        return "tee"
    return "straight" if open_sides[0] == open_sides[2] else "turn"


def _meet(row: _TileLine, column: _TileLine) -> bool:
    """Whether `row` and `column` meet: each reaches the other's middle line."""
    in_row = column.at >= row.from_ - EPSILON and column.at <= row.to + EPSILON
    return in_row and row.at >= column.from_ - EPSILON and row.at <= column.to + EPSILON


def _ways(row: _TileLine, column: _TileLine) -> list[bool]:
    """Which ways the streets leave the junction of `row` and `column`: +Z, +X, -Z, -X."""
    return [
        column.to > row.at + EPSILON,
        row.to > column.at + EPSILON,
        column.from_ < row.at - EPSILON,
        row.from_ < column.at - EPSILON,
    ]


def _junction(row: _TileLine, column: _TileLine) -> RoadPiece | None:
    """The junction piece where `row` and `column` meet, or None. It is the wider road's size; the
    narrower road enters it on whole tiles, the piece starting on a multiple of its size."""
    if not _meet(row, column):
        return None
    size = max(row.size, column.size)
    row_wider = row.size >= column.size
    x = size * math.floor(column.start / size) if row_wider else column.start
    z = row.start if row_wider else size * math.floor(row.start / size)
    across = PieceSide(column.size, column.start - x)
    along = PieceSide(row.size, row.start - z)
    sides: list[PieceSide | None] = []
    for i, is_open in enumerate(_ways(row, column)):
        if not is_open:
            sides.append(None)
        else:
            sides.append(across if i % 2 == 0 else along)
    return RoadPiece(x, z, size, _kind_of(sides), row.size != column.size, sides)


def _junctions(rows: Sequence[_TileLine], columns: Sequence[_TileLine]) -> list[RoadPiece]:
    """The junctions of `rows` and `columns`. Two streets of one line may meet at a junction
    (where the runout's streets go on from those before it): one piece, with the open sides of
    both."""
    # The pieces in the order their keys were first set (a Map keeps that order).
    found: list[RoadPiece] = []
    position: dict[str, int] = {}
    for row in rows:
        for column in columns:
            piece = _junction(row, column)
            if piece is None:
                continue
            key = str(tile_key(piece.x, piece.z))
            if key in position:
                other = found[position[key]]
                sides: list[PieceSide | None] = []
                for i, s in enumerate(piece.sides):
                    sides.append(s if s is not None else other.sides[i])
            else:
                sides = piece.sides
            replaced = RoadPiece(
                piece.x, piece.z, piece.size, _kind_of(sides), piece.adapter, sides
            )
            if key in position:
                found[position[key]] = replaced
            else:
                position[key] = len(found)
                found.append(replaced)
    return found


def _straights(line: _TileLine, tile: TileRules, taken: dict[str, bool]) -> list[RoadPiece]:
    """Straight pieces of `line`, N × N tiles on its own N-tile lattice, where nothing is taken."""
    n = line.size
    side = PieceSide(n, 0)
    sides: list[PieceSide | None] = (
        [None, side, None, side] if line.row else [side, None, side, None]
    )
    pieces: list[RoadPiece] = []
    last = math.floor(line.to / tile.size)
    a = n * math.floor(math.floor(line.from_ / tile.size) / n)
    while a <= last:
        x, z = (a, line.start) if line.row else (line.start, a)
        if str(tile_key(x, z)) not in taken:
            pieces.append(RoadPiece(x, z, n, "straight", False, sides))
        a += n
    return pieces


def road_pieces(roads: Sequence[Road], tile: TileRules) -> list[RoadPiece]:
    """The road pieces of the streets of `roads` (phase 15): the junctions, then straight pieces of
    N × N tiles over the rest of each street."""
    lines: list[_TileLine] = []
    for r in roads:
        if r.kind == "street":
            line = _line_of(r, tile)
            if line is not None:
                lines.append(line)
    pieces = _junctions(
        [line for line in lines if line.row],
        [line for line in lines if not line.row],
    )
    taken = road_tiles(pieces)
    for line in lines:
        more = _straights(line, tile, taken)
        for p in more:
            for k in list(road_tiles([p]).keys()):
                taken[k] = True
        pieces.extend(more)
    return pieces


def road_tiles(pieces: Sequence[RoadPiece]) -> dict[str, bool]:
    """The tiles the pieces cover, as a set of keys (see the module doc)."""
    tiles: dict[str, bool] = {}
    for p in pieces:
        for i in range(p.size):
            for j in range(p.size):
                tiles[str(tile_key(p.x + i, p.z + j))] = True
    return tiles


class PieceCache:
    """The road pieces of the last list of roads asked for, found once (they are asked for every
    chunk). Keyed by the list's identity, as the TypeScript `WeakMap` is (the tile grid is not part
    of the key)."""

    def __init__(self) -> None:
        self._roads: Sequence[Road] | None = None
        self._pieces: list[RoadPiece] = []

    def get(self, roads: Sequence[Road], tile: TileRules) -> list[RoadPiece]:
        """The road pieces of `roads`, worked out on first use."""
        if self._roads is None or self._roads is not roads:
            self._pieces = road_pieces(roads, tile)
            self._roads = roads
        return self._pieces


_PIECE_CACHE = PieceCache()


def cached_road_pieces(roads: Sequence[Road], tile: TileRules) -> list[RoadPiece]:
    """`road_pieces` of `roads`, made once per list of roads."""
    return _PIECE_CACHE.get(roads, tile)
