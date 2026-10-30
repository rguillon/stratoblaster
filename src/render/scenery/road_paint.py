"""A road piece painted pixel by pixel for the road atlas (phase 15, reviewer 2026-10-28: better
looking corners, T and X). The roadway's corners are rounded with distance fields: the sidewalk
corners into a junction get a kerb radius, and the outside of a turn sweeps round. Junctions of
three or four ways get zebra crossings on their arms, the lane lines stopping before them.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from render.scenery.tile_road_geometry import Arm, TileRoadLook, arm_lines, piece_roadway  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.scenery.road_tiles import RoadPiece  # noqa: E402
from core.scenery.scenery_level import TileRules  # noqa: E402

Rgb = tuple[float, float, float]
Rect = tuple[float, float, float, float]
__pragma__("noskip")

# Radius of the sidewalk corners into a junction, in world units.
KERB_RADIUS = 3

# Zebra crossings: depth along the arm, stripe width and gap, gap before the lines.
ZEBRA_DEPTH = 3
ZEBRA_STRIPE = 0.6
ZEBRA_GAP = 0.6
ZEBRA_BEFORE = 1

INF = float("Infinity")


def _hypot(a: float, b: float) -> float:
    """`Math.hypot(a, b)`: JavaScript's rounding, not `math.hypot`."""
    __pragma__("js", "{}", "return Math.hypot(a, b);")
    return 0


def _fround(x: float) -> float:
    """`Math.fround(x)`: the nearest 32-bit float."""
    __pragma__("js", "{}", "return Math.fround(x);")
    return 0


def _round(x: float) -> int:
    """`Math.round(x)`: halves go up, as in JavaScript."""
    return math.floor(x + 0.5)


class Canvas:
    """A grid of pixels larger than the piece by `margin` on every side, where arms run on."""

    def __init__(self, scale: float, margin: int, side: int) -> None:
        """`scale`: pixels per world unit. `margin`: pixels on each side. `side`: side of the
        canvas in pixels."""
        self.scale = scale
        self.margin = margin
        self.side = side


def _envelope(f: list[float]) -> tuple[list[int], list[float], int]:
    """The lower envelope of the parabolas of `f`'s finite values: their apexes and boundaries."""
    n = len(f)
    v = [0 for _ in range(n)]
    z = [0.0 for _ in range(n + 1)]

    def at(i: int) -> float:
        return f[i]

    def meet(p: int, q: int) -> float:
        return (at(q) + q * q - (at(p) + p * p)) / (2 * q - 2 * p)

    k = -1
    for q in range(n):
        if at(q) == INF:
            continue
        while k >= 0 and meet(v[k], q) <= z[k]:
            k -= 1
        k += 1
        v[k] = q
        z[k] = -INF if k == 0 else meet(v[k - 1], q)
        z[k + 1] = INF
    return v, z, k + 1


def _line_1d(f: list[float]) -> list[float]:
    """Squared distances along one line (Felzenszwalb and Huttenlocher)."""
    n = len(f)
    d = [INF for _ in range(n)]
    v, z, count = _envelope(f)
    if count == 0:
        return d
    j = 0
    for q in range(n):
        while z[j + 1] < q:
            j += 1
        p = v[j]
        d[q] = (q - p) * (q - p) + f[p]
    return d


def _distance_to(mask: list[int], side: int) -> list[float]:
    """Exact distance (in pixels) from each pixel to the nearest pixel of `mask`."""
    grid = [0.0 if m else INF for m in mask]
    line = [0.0 for _ in range(side)]
    for stride, step in [(side, 1), (1, side)]:
        for a in range(side):
            for b in range(side):
                line[b] = grid[a * stride + b * step]
            d = _line_1d(line)
            for b in range(side):
                grid[a * stride + b * step] = d[b]
    return [_fround(math.sqrt(g)) for g in grid]


def _within(mask: list[int], side: int, r: float) -> list[int]:
    return [1 if v <= r else 0 for v in _distance_to(mask, side)]


def _invert(mask: list[int]) -> list[int]:
    return [1 - v for v in mask]


def _close(mask: list[int], side: int, r: float) -> list[int]:
    """`mask` with its concave corners rounded to radius `r` (a closing)."""
    return _invert(_within(_invert(_within(mask, side, r)), side, r))


def _pixel(v: float, c: Canvas) -> int:
    return _round(v * c.scale) + c.margin


def _fill(mask: list[Any], c: Canvas, rect: Rect, value: object) -> None:
    """Sets the pixels of `rect` (piece frame, world units) in `mask`."""
    x0, x1, z0, z1 = rect
    if x1 <= x0 or z1 <= z0:
        return
    i0 = _pixel(x0, c)
    i1 = max(_pixel(x1, c), i0 + 1)
    j0 = _pixel(z0, c)
    j1 = max(_pixel(z1, c), j0 + 1)
    for j in range(max(0, j0), min(c.side, j1)):
        for i in range(max(0, i0), min(c.side, i1)):
            mask[j * c.side + i] = value


def _road_mask(piece: RoadPiece, tile: TileRules, c: Canvas) -> list[int]:
    """The roadway, with the arms run on past the edges of the piece so they stay straight there."""
    mask = [0 for _ in range(c.side * c.side)]
    size = piece.size * tile.size
    out = c.margin / c.scale
    roadway, _arms = piece_roadway(piece, tile)
    for rect in roadway:
        _fill(mask, c, rect, 1)
    for i in range(len(piece.sides)):
        s = piece.sides[i]
        if not s:
            continue
        a = s.offset * tile.size + tile.sidewalk
        b = (s.offset + s.size) * tile.size - tile.sidewalk
        run: list[Rect] = [
            (a, b, size, size + out),
            (size, size + out, a, b),
            (a, b, -out, 0),
            (-out, 0, a, b),
        ]
        _fill(mask, c, run[i], 1)
    return mask


def _crossing(
    line: Rect,
    along_x: bool,
    size: float,
) -> tuple[Rect, Rect] | None:
    """Where the lines of an arm stop for its zebra crossing, and the crossing (line, zebra); None
    on a through road, or an arm too short for one."""
    x0, x1, z0, z1 = line
    p0 = x0 if along_x else z0
    p1 = x1 if along_x else z1
    at_start = p1 >= size - 1e-6 and p0 > 1e-6  # noqa: PLR2004
    at_end = p0 <= 1e-6 and p1 < size - 1e-6  # noqa: PLR2004
    if not at_start and not at_end:
        return None
    # As deep as the arm allows, short of the edge; none on an arm too short for one.
    z = min(ZEBRA_DEPTH, p1 - p0 - 0.4)
    if z < 1:
        return None
    if at_start:
        zebra = (p0, p0 + z)
        rest = (p0 + z + ZEBRA_BEFORE, p1)
    else:
        zebra = (p1 - z, p1)
        rest = (p0, p1 - z - ZEBRA_BEFORE)
    return _span_rect(rest, along_x, line), _span_rect(zebra, along_x, line)


def _span_rect(span: tuple[float, float], along_x: bool, line: Rect) -> Rect:
    """The rectangle of `line` cut to `span` along the arm."""
    x0, x1, z0, z1 = line
    a, b = span
    if along_x:
        return (a, b, z0, z1)
    return (x0, x1, a, b)


def _stripes(rect: Rect, along_x: bool) -> list[Rect]:
    """The zebra stripes of `rect`, running along the arm, across its width."""
    x0, x1, z0, z1 = rect
    a = z0 if along_x else x0
    b = z1 if along_x else x1
    out: list[Rect] = []
    c = a + ZEBRA_GAP
    while c + ZEBRA_STRIPE <= b - ZEBRA_GAP / 2:
        if along_x:
            out.append((x0, x1, c, c + ZEBRA_STRIPE))
        else:
            out.append((c, c + ZEBRA_STRIPE, z0, z1))
        c += ZEBRA_STRIPE + ZEBRA_GAP
    return out


def _paint_lines(
    pixels: list[Any],
    piece: RoadPiece,
    tile: TileRules,
    look: TileRoadLook,
    c: Canvas,
) -> None:
    """The lane lines of the arms, and zebra crossings on those of a T or an X."""
    size = piece.size * tile.size
    junction = piece.kind == "tee" or piece.kind == "cross"  # noqa: PLR1714
    _roadway, arms = piece_roadway(piece, tile)
    for arm in arms:
        cut = _crossing(arm.line, arm.along_x, size) if junction else None
        line = cut[0] if cut is not None else arm.line
        centre, lanes = arm_lines(Arm(arm.lanes, line, arm.along_x), look.lineWidth)
        for rect in lanes:
            _fill(pixels, c, rect, look.laneLine)
        for rect in centre:
            _fill(pixels, c, rect, look.centreLine)
        if cut is not None:
            for rect in _stripes(cut[1], arm.along_x):
                _fill(pixels, c, rect, look.laneLine)


def _paint_turn(piece: RoadPiece, tile: TileRules, look: TileRoadLook, n: int) -> list[Any]:
    """A turn, drawn as a quarter ring round the corner its two open sides share: the roadway
    keeps its width round the bend, and its lines follow it as arcs."""
    size = piece.size * tile.size
    cx = size if piece.sides[1] else 0
    cz = size if piece.sides[0] else 0
    inner = tile.sidewalk
    outer = size - tile.sidewalk
    lane = (outer - inner) / (2 * piece.size)
    half = look.lineWidth / 2
    arcs: list[tuple[float, Rgb]] = [(size / 2, look.centreLine)]
    for k in range(1, piece.size):
        arcs.append((size / 2 - k * lane, look.laneLine))
        arcs.append((size / 2 + k * lane, look.laneLine))

    def colour(r: float) -> Rgb:
        if r >= inner and r <= outer:
            for at, col in arcs:
                if abs(r - at) <= half:
                    return col
            return look.roadway
        kerb = r >= inner - look.kerbWidth and r <= outer + look.kerbWidth
        return look.kerb if kerb else look.sidewalk

    out: list[Any] = []
    for j in range(n):
        for i in range(n):
            dx = ((i + 0.5) / n) * size - cx
            dz = ((j + 0.5) / n) * size - cz
            out.append(colour(_hypot(dx, dz)))
    return out


def _rounded_road(piece: RoadPiece, tile: TileRules, c: Canvas) -> list[int]:
    """The roadway of `piece`, the sidewalk corners into its junction rounded to the kerb radius."""
    return _close(_road_mask(piece, tile, c), c.side, KERB_RADIUS * c.scale)


def paint_piece(
    piece: RoadPiece,
    tile: TileRules,
    look: TileRoadLook,
    n: int,
) -> list[Any]:
    """The colour of each pixel of `piece`, `n` x `n`, row by row along +Z."""
    if piece.kind == "turn":
        return _paint_turn(piece, tile, look, n)
    scale = n / (piece.size * tile.size)
    margin = math.ceil((KERB_RADIUS + look.kerbWidth) * 2 * scale)
    c = Canvas(scale, margin, n + 2 * margin)
    road = _rounded_road(piece, tile, c)
    kerb = _within(road, c.side, look.kerbWidth * scale)
    pixels = [
        look.roadway if road[i] else (look.kerb if kerb[i] else look.sidewalk)
        for i in range(c.side * c.side)
    ]
    _paint_lines(pixels, piece, tile, look, c)
    out: list[Any] = []
    for j in range(n):
        for i in range(n):
            v = pixels[(j + margin) * c.side + i + margin]
            out.append(v if v else look.sidewalk)
    return out
