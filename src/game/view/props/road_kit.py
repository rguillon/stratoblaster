"""The road kit, for the `props/` page (Phase 15, P15-R03, R04, R10), ported from
`props/road-kit.ts`: a straight, a 90° turn, a T and an X for each size, the T and X adapters for
each pair of sizes, and a sample layout where each piece is joined to the straights of its open
sides."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from core.scenery.road_tiles import PieceSide, RoadPiece  # noqa: E402
from game.config.scenery_look import BASE_SCENERY_LOOK  # noqa: E402
from game.config.tile_buildings import TILE  # noqa: E402
from render.geometry.gradient_shapes import ColoredGeometry  # noqa: E402
from render.scenery.scenery_look import PropGeometry  # noqa: E402
from render.scenery.tile_road_geometry import add_piece  # noqa: E402

# The render code reads the look's camelCase fields, so the config record is the look itself.
LOOK = BASE_SCENERY_LOOK.roads.tiles
# Road sizes of the kit: up to 3 × 3 (the 4 × 4 roads dropped, reviewer 2026-10-28).
SIZES = [1, 2, 3]

# Id of the sample layout.
ROAD_SAMPLE_ID = "road-sample"

# Steps to the next piece beyond side `i` (+Z, +X, -Z, -X).
STEPS = [[0, 1], [1, 0], [0, -1], [-1, 0]]


class KitPiece:
    """A named piece of the kit, at tile (0, 0)."""

    def __init__(self, piece_id: str, piece: RoadPiece) -> None:
        self.id = piece_id
        self.piece = piece


def side(size: int, offset: int = 0) -> PieceSide:
    """An open side of a piece `size` tiles wide, `offset` tiles from the low edge."""
    return PieceSide(size, offset)


def kit_piece(piece_id: str, size: int, sides: list[Any], kind: str) -> KitPiece:
    """A kit piece of `size` tiles, with the open `sides` (None where closed)."""
    adapter = False
    for s in sides:
        if s != None and s.size != size:  # noqa: E711 (undefined or null: a closed side)
            adapter = True
    return KitPiece(piece_id, RoadPiece(0, 0, size, kind, adapter, sides))


def make_pieces() -> list[KitPiece]:
    """The 12 pieces of the sizes (4 each): straight (along Z), turn, T and X, for each size."""
    pieces: list[KitPiece] = []
    for n in SIZES:
        s = side(n)
        pieces.append(kit_piece("road-straight-" + str(n), n, [s, None, s, None], "straight"))
        pieces.append(kit_piece("road-turn-" + str(n), n, [s, s, None, None], "turn"))
        pieces.append(kit_piece("road-tee-" + str(n), n, [None, s, s, s], "tee"))
        pieces.append(kit_piece("road-cross-" + str(n), n, [s, s, s, s], "cross"))
    return pieces


def make_adapters() -> list[KitPiece]:
    """The adapters: for each pair N > M, the size-M road ending on (T) or crossing (X) the
    size-N road, which runs along X; the narrow road as close to the middle as the grid allows."""
    adapters: list[KitPiece] = []
    for n in SIZES:
        for m in SIZES:
            if m < n:
                wide = side(n)
                narrow = side(m, math.floor((n - m) / 2))
                name = str(n) + "-" + str(m)
                adapters.append(kit_piece("road-tee-" + name, n, [None, wide, narrow, wide], "tee"))
                adapters.append(
                    kit_piece("road-cross-" + name, n, [narrow, wide, narrow, wide], "cross")
                )
    return adapters


def make_kit() -> list[KitPiece]:
    """The pieces of the kit, then its adapters (`list + list` would concatenate strings)."""
    kit = make_pieces()
    kit.extend(make_adapters())
    return kit


ROAD_KIT = make_kit()


def flat(_x: float, _z: float) -> float:
    """Flat ground: no height."""
    return 0


def geometry_of(pieces: list[RoadPiece]) -> PropGeometry:
    """`pieces` drawn on flat ground, centred on the origin."""
    geo = ColoredGeometry()
    for p in pieces:
        add_piece(geo, p, TILE, LOOK, flat)
    xs: list[float] = []
    zs: list[float] = []
    for p in pieces:
        xs.append(p.x)
        xs.append(p.x + p.size)
        zs.append(p.z)
        zs.append(p.z + p.size)
    cx = ((min(xs) + max(xs)) / 2) * TILE.size
    cz = ((min(zs) + max(zs)) / 2) * TILE.size
    positions = geo.positions
    for i in range(0, len(positions), 3):
        positions[i] = positions[i] - cx
        positions[i + 2] = positions[i + 2] - cz
    return PropGeometry(geo)


def with_stubs(piece: RoadPiece, x: int, z: int) -> list[RoadPiece]:
    """The straight pieces joined to each open side of `piece`, at (x, z)."""
    placed = RoadPiece(x, z, piece.size, piece.kind, piece.adapter, piece.sides)
    result: list[RoadPiece] = [placed]
    for i, s in enumerate(piece.sides):
        if s == None:  # noqa: E711 (undefined or null: a closed side)
            continue
        step = STEPS[i]
        dx = step[0]
        dz = step[1]
        along_z = dz != 0
        sides: list[Any] = (
            [side(s.size), None, side(s.size), None]
            if along_z
            else [None, side(s.size), None, side(s.size)]
        )
        if along_z:
            sx = x + s.offset
        elif dx > 0:
            sx = x + piece.size
        else:
            sx = x - s.size
        sz = (z + piece.size if dz > 0 else z - s.size) if along_z else z + s.offset
        result.append(RoadPiece(sx, sz, s.size, "straight", False, sides))
    return result


def sample_pieces() -> list[RoadPiece]:
    """The sample layout's pieces: every piece of the kit with straights on its open sides."""
    cell = 4 + 2 * max(SIZES)
    columns = 7
    result: list[RoadPiece] = []
    for i, kit in enumerate(ROAD_KIT):
        result.extend(with_stubs(kit.piece, (i % columns) * cell, math.floor(i / columns) * cell))
    return result


def centred(pieces: list[RoadPiece]) -> list[RoadPiece]:
    """`pieces` moved so their middle is at the origin (in tiles; may be a half tile off)."""
    xs: list[float] = []
    zs: list[float] = []
    for p in pieces:
        xs.append(p.x)
        xs.append(p.x + p.size)
        zs.append(p.z)
        zs.append(p.z + p.size)
    cx = (min(xs) + max(xs)) / 2
    cz = (min(zs) + max(zs)) / 2
    # Half-tile offsets: the core types a piece's position as int, the page draws it centred.
    return [
        RoadPiece(p.x - cx, p.z - cz, p.size, p.kind, p.adapter, p.sides)  # type: ignore[arg-type]
        for p in pieces
    ]


def build_sample() -> PropGeometry:
    """The sample layout (P15-R10): every piece of the kit with straights on its open sides."""
    return geometry_of(sample_pieces())


def make_kit_pieces_map() -> dict[str, list[RoadPiece]]:
    """The pieces of each model of the kit, centred as the models are: the `props/` page draws
    them as textured surfaces, like the levels (phase 15)."""
    result: dict[str, list[RoadPiece]] = {}
    for kit in ROAD_KIT:
        result[kit.id] = centred([kit.piece])
    result[ROAD_SAMPLE_ID] = centred(sample_pieces())
    return result


ROAD_KIT_PIECES = make_kit_pieces_map()


def piece_model(piece: RoadPiece) -> Any:  # noqa: ANN401 (a model factory)
    """A model factory for one kit piece, drawn on flat ground."""

    def make() -> PropGeometry:
        return geometry_of([piece])

    return make


def make_kit_models() -> dict[str, Any]:
    """The road kit and its sample layout, as models for the `props/` page."""
    result: dict[str, Any] = {}
    for kit in ROAD_KIT:
        result[kit.id] = piece_model(kit.piece)
    result[ROAD_SAMPLE_ID] = build_sample
    return result


ROAD_KIT_MODELS = make_kit_models()


def make_kit_notes() -> dict[str, str]:
    """What each piece is, shown after its name."""
    result: dict[str, str] = {}
    for kit in ROAD_KIT:
        size = str(kit.piece.size)
        result[kit.id] = size + "×" + size + (" adapter" if kit.piece.adapter else "")
    return result


ROAD_KIT_NOTES = make_kit_notes()
