"""Road pieces of the districts on tiles (phase 15, P15-R02, P15-R03, P15-R04): a sidewalk over the
whole piece, a kerb and the roadway of each open side, joined in the middle, and the lane markings
up to the junction. Draped on the ground, so pieces meet with no step.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.gradient_shapes import ColoredGeometry

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402

from core.scenery.road_tiles import PieceSide, RoadPiece  # noqa: E402
from core.scenery.scenery_level import TileRules  # noqa: E402

Rgb = tuple[float, float, float]
Height = Callable[[float, float], float]
Rect = tuple[float, float, float, float]
__pragma__("noskip")

# Layers above the sidewalk, so the kerb, the roadway and the lines each show over the last.
LAYER = 0.1

# How each side's arm runs, in the order of `PieceSides` (+Z, +X, -Z, -X): whether it runs along
# X, and from which edge (the high one or the low one).
ARMS = [(False, True), (True, True), (False, False), (True, False)]


def _hypot(a: float, b: float) -> float:
    """`Math.hypot(a, b)`: JavaScript's rounding, not `math.hypot`."""
    __pragma__("js", "{}", "return Math.hypot(a, b);")
    return 0


class TileRoadLook:
    """How the road pieces look."""

    def __init__(  # noqa: PLR0917
        self,
        roadway: Rgb,
        sidewalk: Rgb,
        kerb: Rgb,
        kerb_width: float,
        centre_line: Rgb,
        lane_line: Rgb,
        line_width: float,
        lift: float,
    ) -> None:
        self.roadway = roadway
        self.sidewalk = sidewalk
        self.kerb = kerb
        """Width of the kerb along the roadway's edges."""
        self.kerbWidth = kerb_width
        self.centreLine = centre_line
        self.laneLine = lane_line
        self.lineWidth = line_width
        """Height of the sidewalks above the ground."""
        self.lift = lift


class Arm:
    """An arm of a piece: its roadway up to the junction, where its lines stop."""

    def __init__(self, lanes: int, line: Rect, along_x: bool) -> None:
        self.lanes = lanes
        self.line = line
        self.along_x = along_x


def _min_of(values: list[float]) -> float:
    result = values[0]
    for v in values:
        result = min(result, v)
    return result


def _max_of(values: list[float]) -> float:
    result = values[0]
    for v in values:
        result = max(result, v)
    return result


def _roadway_of(side: PieceSide, tile: TileRules) -> list[float]:
    """Where the roadway of an open side runs across the piece, from its low edge."""
    return [
        side.offset * tile.size + tile.sidewalk,
        (side.offset + side.size) * tile.size - tile.sidewalk,
    ]


def _span_of(sides: list[PieceSide | None], tile: TileRules) -> list[float] | None:
    """The span of the roadways of `sides` across the piece, if any of them is open."""
    spans: list[list[float]] = []
    for s in sides:
        if s:
            spans.append(_roadway_of(s, tile))
    if len(spans) == 0:
        return None
    return [_min_of([p[0] for p in spans]), _max_of([p[1] for p in spans])]


def _arm_rect(to: float, along_x: bool, high: bool, size: float, a: float, b: float) -> Rect:
    """The rectangle of an arm from its edge to `to`, across the roadway (a, b)."""
    lo = to if high else 0
    hi = size if high else to
    if along_x:
        return (lo, hi, a, b)
    return (a, b, lo, hi)


def _arm_of(
    side: PieceSide,
    along_x: bool,
    high: bool,
    across: list[float] | None,
    size: float,
    tile: TileRules,
) -> tuple[Rect, Rect]:
    """The roadway of an open side, from its edge to the far side of the roads `across` it (or
    right across without one), and the rectangle its lines stop in, at their near side."""
    roadway = _roadway_of(side, tile)
    a = roadway[0]
    b = roadway[1]
    if across is not None:
        lo = across[0]
        hi = across[1]
    elif high:
        lo = 0
        hi = 0
    else:
        lo = size
        hi = size
    far = lo if high else hi
    near = hi if high else lo
    rect = _arm_rect(far, along_x, high, size, a, b)
    line = _arm_rect(near, along_x, high, size, a, b)
    return rect, line


def piece_roadway(piece: RoadPiece, tile: TileRules) -> tuple[list[Rect], list[Arm]]:
    """The roadway of a piece and the lines of its arms, as rectangles: each open side's roadway
    runs from its edge to the far side of the roads across it (or right across without one), and
    its lines stop at their near side."""
    size = piece.size * tile.size
    # The roads across each way: those along Z span X, those along X span Z.
    spans_x = _span_of([piece.sides[0], piece.sides[2]], tile)
    spans_z = _span_of([piece.sides[1], piece.sides[3]], tile)
    roadway: list[Rect] = []
    arms: list[Arm] = []
    for i in range(len(piece.sides)):
        side = piece.sides[i]
        if not side:
            continue
        along_x = ARMS[i][0]
        high = ARMS[i][1]
        across = spans_x if along_x else spans_z
        rect, line = _arm_of(side, along_x, high, across, size, tile)
        roadway.append(rect)
        arms.append(Arm(side.size, line, along_x))
    return roadway, arms


def _at_line(arm: Arm, c: float, width: float) -> Rect:
    x0, x1, z0, z1 = arm.line
    if arm.along_x:
        return (x0, x1, c - width / 2, c + width / 2)
    return (c - width / 2, c + width / 2, z0, z1)


def arm_lines(arm: Arm, width: float) -> tuple[list[Rect], list[Rect]]:
    """The line rectangles of an arm: the centre line, and lane lines on wide roads. Returns
    (centre, lanes)."""
    x0, x1, z0, z1 = arm.line
    if arm.along_x:
        a = z0
        b = z1
    else:
        a = x0
        b = x1
    lane = (b - a) / (2 * arm.lanes)
    mid = (a + b) / 2
    lanes: list[Rect] = []
    for k in range(1, arm.lanes):
        lanes.append(_at_line(arm, mid - k * lane, width))
        lanes.append(_at_line(arm, mid + k * lane, width))
    return [_at_line(arm, mid, width)], lanes


def cuts(a: float, b: float, cell: float) -> list[float]:
    """The cuts of [a, b] (world units): its ends, and every multiple of `cell` between them. All
    the layers of the roads are cut on the same world lattice, so their vertices line up and,
    draped on uneven ground, one layer never bulges through the one above it (z-fighting on the
    wide roads of World 4, reviewer 2026-10-28)."""
    out = [a]
    c = (math.floor(a / cell) + 1) * cell
    while c < b - 1e-6:
        out.append(c)
        c += cell
    out.append(b)
    return out


def _add_rect(  # noqa: PLR0917
    geo: ColoredGeometry,
    rect: Rect,
    ox: float,
    oz: float,
    height: Height,
    color: Rgb,
    cell: float,
) -> None:
    """Appends `rect` (piece frame) to `geo`, cut on the world lattice of `cell`, draped on
    `height(x, z)`."""
    x0, x1, z0, z1 = rect
    if x1 - x0 <= 0 or z1 - z0 <= 0:
        return
    xs = cuts(ox + x0, ox + x1, cell)
    zs = cuts(oz + z0, oz + z1, cell)
    base = len(geo.positions) // 3
    for z in zs:
        for x in xs:
            geo.positions.extend([x, height(x, z), z])
            geo.colors.extend([color[0], color[1], color[2], 1])
    nx = len(xs) - 1
    for j in range(len(zs) - 1):
        for i in range(nx):
            a = base + j * (nx + 1) + i
            b = a + 1
            c = a + nx + 1
            d = c + 1
            # Facing up (Babylon's front faces).
            geo.indices.extend([a, b, c, b, d, c])


def _layer_height(ground: Height, lift: float, layer: float) -> Height:
    """The height of a layer above the ground under it."""

    def height(x: float, z: float) -> float:
        return ground(x, z) + lift + layer * LAYER

    return height


def add_piece(
    geo: ColoredGeometry,
    piece: RoadPiece,
    tile: TileRules,
    look: TileRoadLook,
    ground: Height,
) -> None:
    """Appends the geometry of `piece` to `geo`, at `ground(x, z)` of the ground under it (world
    coordinates; flat ground at 0 for the `props/` page)."""
    size = piece.size * tile.size
    ox = piece.x * tile.size
    oz = piece.z * tile.size
    cell = tile.size / 2
    _add_rect(
        geo, (0, size, 0, size), ox, oz, _layer_height(ground, look.lift, 0), look.sidewalk, cell
    )
    roadway, arms = piece_roadway(piece, tile)
    k = look.kerbWidth
    for x0, x1, z0, z1 in roadway:
        kerb = (max(0, x0 - k), min(size, x1 + k), max(0, z0 - k), min(size, z1 + k))
        _add_rect(geo, kerb, ox, oz, _layer_height(ground, look.lift, 1), look.kerb, cell)
    for rect in roadway:
        _add_rect(geo, rect, ox, oz, _layer_height(ground, look.lift, 2), look.roadway, cell)
    for arm in arms:
        centre, lanes = arm_lines(arm, look.lineWidth)
        for rect in centre:
            _add_rect(geo, rect, ox, oz, _layer_height(ground, look.lift, 3), look.centreLine, cell)
        for rect in lanes:
            _add_rect(geo, rect, ox, oz, _layer_height(ground, look.lift, 3), look.laneLine, cell)


def build_tile_grid(
    pieces: list[RoadPiece],
    tile: TileRules,
    ground: Height,
    z_min: float,
    z_max: float,
    color: Rgb,
) -> ColoredGeometry:
    """P15-R10 (`tiles=1`): thin lines along the tile edges over the districts whose pieces are in
    [z_min, z_max), from one end of their pieces to the other."""
    geo = ColoredGeometry()
    in_chunk: list[RoadPiece] = []
    for p in pieces:
        mid = (p.z + p.size / 2) * tile.size
        if mid >= z_min and mid < z_max:
            in_chunk.append(p)
    if len(in_chunk) == 0:
        return geo
    x0 = _min_of([p.x for p in in_chunk])
    x1 = _max_of([p.x + p.size for p in in_chunk])
    z0 = _min_of([p.z for p in in_chunk])
    z1 = _max_of([p.z + p.size for p in in_chunk])
    width = 0.25
    t = tile.size
    above = _above_ground(ground)
    for i in range(int(x0), int(x1) + 1):
        _add_rect(geo, (i * t - width, i * t + width, z0 * t, z1 * t), 0, 0, above, color, t)
    for j in range(int(z0), int(z1) + 1):
        _add_rect(geo, (x0 * t, x1 * t, j * t - width, j * t + width), 0, 0, above, color, t)
    return geo


def _above_ground(ground: Height) -> Height:
    """The ground plus one world unit, for the grid lines."""

    def height(x: float, z: float) -> float:
        return ground(x, z) + 1

    return height


def build_tile_road_geometry(
    pieces: list[RoadPiece],
    tile: TileRules,
    look: TileRoadLook,
    ground: Height,
    z_min: float,
    z_max: float,
) -> ColoredGeometry:
    """The pieces of `pieces` whose middle is in [z_min, z_max), on `ground`."""
    geo = ColoredGeometry()
    for piece in pieces:
        mid = (piece.z + piece.size / 2) * tile.size
        if mid >= z_min and mid < z_max:
            add_piece(geo, piece, tile, look, ground)
    return geo
