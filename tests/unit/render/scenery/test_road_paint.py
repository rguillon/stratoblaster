# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/road_paint.py` (GFX-ROAD-20)."""

import math

import pytest

from core.math.rng import create_rng
from core.scenery.road_tiles import PieceSide, RoadPiece
from core.scenery.scenery_level import TileRules
from render.scenery.road_paint import (
    INF,
    KERB_RADIUS,
    Canvas,
    _close,
    _crossing,
    _distance_to,
    _fround,
    _invert,
    _paint_lines,
    _road_mask,
    _rounded_road,
    _within,
    paint_piece,
)
from render.scenery.tile_road_geometry import TileRoadLook

GREY = (0.5, 0.5, 0.5)
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)
RED = (1.0, 0.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
TILE = TileRules(10, 2)
LOOK = TileRoadLook(GREY, WHITE, BLACK, 0.5, RED, BLUE, 0.3, 0.1)


def _piece(sides: list[PieceSide | None], kind: str, size: int = 1) -> RoadPiece:
    return RoadPiece(0, 0, size, kind, adapter=False, sides=sides)


def _straight() -> RoadPiece:
    return _piece([PieceSide(1, 0), None, PieceSide(1, 0), None], "straight")


def _cross() -> RoadPiece:
    return _piece([PieceSide(1, 0)] * 4, "cross")


def _turn() -> RoadPiece:
    return _piece([PieceSide(1, 0), PieceSide(1, 0), None, None], "turn")


def _pixel(pixels: list, n: int, i: int, j: int) -> tuple[float, ...]:
    """Return the colour of the pixel in column `i` (along X) and row `j` (along Z).

    The piece is n x n.
    """
    return pixels[j * n + i]


def test_the_distance_map_is_exact_from_a_single_pixel() -> None:
    side = 5
    mask = [0] * (side * side)
    mask[2 * side + 2] = 1
    d = _distance_to(mask, side)
    assert d[2 * side + 2] == 0
    assert d[2 * side + 0] == pytest.approx(2)
    assert d[0] == pytest.approx(math.sqrt(8), rel=1e-6)


def test_within_keeps_the_pixels_at_most_the_radius_from_the_mask() -> None:
    side = 5
    mask = [0] * (side * side)
    mask[2 * side + 2] = 1
    # Distance 1.5 reaches the 8 neighbours (the diagonals are 1.41 away) and the pixel itself.
    assert sum(_within(mask, side, 1.5)) == 9


def test_closing_fills_the_concave_corner_of_a_notch_and_keeps_the_road() -> None:
    side = 12
    mask = [0 if (x >= 6 and y >= 6) else 1 for y in range(side) for x in range(side)]
    closed = _close(mask, side, 2)
    # The notch's inner corner is filled by a fillet of radius 2; its far part stays open.
    assert closed[6 * side + 6] == 1
    assert closed[9 * side + 9] == 0
    # Closing only adds road: no pixel of the road is lost.
    assert all(c >= m for c, m in zip(closed, mask, strict=True))


def test_a_convex_block_of_road_is_unchanged_by_closing() -> None:
    side = 12
    mask = [1 if (3 <= x <= 8 and 3 <= y <= 8) else 0 for y in range(side) for x in range(side)]
    assert _close(mask, side, 2) == mask


def test_a_straight_piece_is_roadway_down_its_middle_and_sidewalk_at_its_edges() -> None:
    n = 20
    pixels = paint_piece(_straight(), TILE, LOOK, n)
    assert len(pixels) == n * n
    row = n // 2
    assert _pixel(pixels, n, 7, row) == GREY
    assert _pixel(pixels, n, 0, row) == WHITE
    assert _pixel(pixels, n, n - 1, row) == WHITE


def test_a_straight_piece_with_one_lane_each_way_has_its_centre_line_and_no_lane_lines() -> None:
    n = 20
    pixels = paint_piece(_straight(), TILE, LOOK, n)
    # The centre line is at X = 5 (pixel 10 of 20).
    assert _pixel(pixels, n, 10, n // 2) == RED
    assert all(p != BLUE for p in pixels)


def test_a_turn_is_a_quarter_ring_round_the_corner_its_open_sides_share() -> None:
    n = 20
    pixels = paint_piece(_turn(), TILE, LOOK, n)
    corner = (10.0, 10.0)
    half = LOOK.lineWidth / 2
    rings = []
    for j in range(n):
        for i in range(n):
            x = (i + 0.5) / n * 10
            z = (j + 0.5) / n * 10
            r = math.hypot(x - corner[0], z - corner[1])
            if pixels[j * n + i] == RED:
                rings.append(r)
    # The centre line is the arc of radius size / 2 round the corner.
    assert rings
    assert all(abs(r - 5) <= half + 1e-9 for r in rings)
    # The corner the sides share and the far corner are sidewalk.
    assert _pixel(pixels, n, n - 1, n - 1) == WHITE
    assert _pixel(pixels, n, 0, 0) == WHITE


def test_a_cross_is_painted_with_zebra_crossings_on_its_arms() -> None:
    n = 40
    pixels = paint_piece(_cross(), TILE, LOOK, n)
    blue = [k for k, p in enumerate(pixels) if p == BLUE]
    # The zebra stripes are lane-coloured, on the arms only: none on the roadway's middle.
    assert blue
    middle = (n // 2) * n + n // 2
    assert pixels[middle] != BLUE


def test_rounding_the_junction_only_adds_road_at_the_corners_of_a_cross() -> None:
    canvas = Canvas(1.0, 14, 20 + 28)
    raw = _road_mask(_cross(), TILE, canvas)
    rounded = _rounded_road(_cross(), TILE, canvas)
    added = [k for k in range(len(raw)) if rounded[k] and not raw[k]]
    assert added
    assert all(rounded[k] >= raw[k] for k in range(len(raw)))


@pytest.mark.parametrize("kind", ["straight", "turn", "cross"])
def test_paint_piece_returns_one_colour_per_pixel(kind: str) -> None:
    piece = {"straight": _straight(), "turn": _turn(), "cross": _cross()}[kind]
    pixels = paint_piece(piece, TILE, LOOK, 12)
    assert len(pixels) == 144
    assert all(len(p) == 3 for p in pixels)


def test_a_through_road_has_no_zebra_crossing() -> None:
    # The arm runs right across the piece: neither end stops at a junction.
    assert _crossing((0, 10, 4, 6), True, 10) is None
    assert _crossing((4, 6, 0, 10), False, 10) is None


def test_an_arm_too_short_for_a_zebra_crossing_has_none() -> None:
    # 1.2 units long: the crossing would be shallower than one unit.
    assert _crossing((8.8, 10, 4, 6), True, 10) is None
    assert _crossing((4, 6, 0, 1.2), False, 10) is None


def test_an_arm_from_the_edge_has_its_crossing_where_it_meets_the_junction() -> None:
    cut = _crossing((0, 6, 4, 6), True, 10)
    assert cut is not None
    line, zebra = cut
    # The zebra is 3 deep at the arm's junction end; its lines stop a unit before it.
    assert zebra == (3, 6, 4, 6)
    assert line == (0, 2, 4, 6)


def test_a_two_lane_straight_has_lane_lines_either_side_of_its_centre_line() -> None:
    n = 20
    piece = _piece([PieceSide(2, 0), None, PieceSide(2, 0), None], "straight", size=2)
    pixels = paint_piece(piece, TILE, LOOK, n)
    row = [_pixel(pixels, n, i, n // 2) for i in range(n)]
    assert RED in row
    lanes = [i for i, p in enumerate(row) if p == BLUE]
    centre = [i for i, p in enumerate(row) if p == RED]
    assert any(i < min(centre) for i in lanes)
    assert any(i > max(centre) for i in lanes)


def test_a_two_lane_turn_has_lane_arcs_either_side_of_its_centre_arc() -> None:
    n = 40
    piece = _piece([PieceSide(2, 0), PieceSide(2, 0), None, None], "turn", size=2)
    pixels = paint_piece(piece, TILE, LOOK, n)
    size = 20.0
    radii = []
    for j in range(n):
        for i in range(n):
            if pixels[j * n + i] == BLUE:
                x = (i + 0.5) / n * size
                z = (j + 0.5) / n * size
                radii.append(math.hypot(x - size, z - size))
    # The lane arcs are a lane (16 / 4 = 4) inside and outside the centre arc of radius 10.
    assert radii
    assert any(r < 10 for r in radii)
    assert any(r > 10 for r in radii)
    half = LOOK.lineWidth / 2
    assert all(abs(r - 6) <= half + 1e-9 or abs(r - 14) <= half + 1e-9 for r in radii)


# D-418: the distance fields as they were, with list comprehensions, to compare with (PERF-03).


def _reference_envelope(f: list[float]) -> tuple[list[int], list[float], int]:
    n = len(f)
    v = [0 for _ in range(n)]
    z = [0.0 for _ in range(n + 1)]

    def meet(p: int, q: int) -> float:
        return (f[q] + q * q - (f[p] + p * p)) / (2 * q - 2 * p)

    k = -1
    for q in range(n):
        if f[q] == INF:
            continue
        while k >= 0 and meet(v[k], q) <= z[k]:
            k -= 1
        k += 1
        v[k] = q
        z[k] = -INF if k == 0 else meet(v[k - 1], q)
        z[k + 1] = INF
    return v, z, k + 1


def _reference_line(f: list[float]) -> list[float]:
    n = len(f)
    d = [INF for _ in range(n)]
    v, z, count = _reference_envelope(f)
    if count == 0:
        return d
    j = 0
    for q in range(n):
        while z[j + 1] < q:
            j += 1
        p = v[j]
        d[q] = (q - p) * (q - p) + f[p]
    return d


def _reference_distance(mask: list[int], side: int) -> list[float]:
    grid = [0.0 if m else INF for m in mask]
    line = [0.0 for _ in range(side)]
    for stride, step in [(side, 1), (1, side)]:
        for a in range(side):
            for b in range(side):
                line[b] = grid[a * stride + b * step]
            d = _reference_line(line)
            for b in range(side):
                grid[a * stride + b * step] = d[b]
    return [_fround(math.sqrt(g)) for g in grid]


def _reference_within(mask: list[int], side: int, r: float) -> list[int]:
    return [1 if v <= r else 0 for v in _reference_distance(mask, side)]


def _reference_close(mask: list[int], side: int, r: float) -> list[int]:
    inverted = [1 - v for v in _reference_within(mask, side, r)]
    return [1 - v for v in _reference_within(inverted, side, r)]


@pytest.mark.parametrize("seed", [1, 2, 3, 4])
def test_d418_the_distance_fields_match_the_list_comprehensions(seed: int) -> None:
    random = create_rng(seed)
    side = 17
    mask = [1 if random() < 0.15 * seed else 0 for _ in range(side * side)]
    assert _distance_to(mask, side) == _reference_distance(mask, side)
    assert _within(mask, side, 2.5) == _reference_within(mask, side, 2.5)
    assert _close(mask, side, 3.2) == _reference_close(mask, side, 3.2)
    assert _invert(mask) == [1 - v for v in mask]
    empty = [0] * side
    assert _distance_to(empty, 1) == [INF] * side


@pytest.mark.parametrize("kind", ["straight", "tee", "cross"])
def test_d418_a_piece_is_painted_as_with_the_list_comprehensions(kind: str) -> None:
    sides = {
        "straight": [PieceSide(2, 0), None, PieceSide(2, 0), None],
        "tee": [PieceSide(2, 0), PieceSide(2, 0), PieceSide(2, 0), None],
        "cross": [PieceSide(2, 0)] * 4,
    }[kind]
    piece = _piece(sides, kind, 2)
    n = 24
    scale = n / (piece.size * TILE.size)
    margin = math.ceil((KERB_RADIUS + LOOK.kerbWidth) * 2 * scale)
    c = Canvas(scale, margin, n + 2 * margin)
    road = _reference_close(_road_mask(piece, TILE, c), c.side, KERB_RADIUS * c.scale)
    kerb = _reference_within(road, c.side, LOOK.kerbWidth * scale)
    pixels = [
        LOOK.roadway if road[i] else (LOOK.kerb if kerb[i] else LOOK.sidewalk)
        for i in range(c.side * c.side)
    ]
    _paint_lines(pixels, piece, TILE, LOOK, c)
    expected = []
    for j in range(n):
        for i in range(n):
            v = pixels[(j + margin) * c.side + i + margin]
            expected.append(v or LOOK.sidewalk)
    assert paint_piece(piece, TILE, LOOK, n) == expected
