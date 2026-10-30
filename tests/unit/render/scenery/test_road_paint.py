"""Unit tests of `src/render/scenery/road_paint.py`."""

import math

import pytest

from core.scenery.road_tiles import PieceSide, RoadPiece
from core.scenery.scenery_level import TileRules
from render.scenery.road_paint import (
    Canvas,
    _close,
    _distance_to,
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
    return RoadPiece(0, 0, size, kind, False, sides)


def _straight() -> RoadPiece:
    return _piece([PieceSide(1, 0), None, PieceSide(1, 0), None], "straight")


def _cross() -> RoadPiece:
    return _piece([PieceSide(1, 0)] * 4, "cross")


def _turn() -> RoadPiece:
    return _piece([PieceSide(1, 0), PieceSide(1, 0), None, None], "turn")


def _pixel(pixels: list, n: int, i: int, j: int) -> tuple[float, ...]:
    """The colour of the pixel in column `i` (along X) and row `j` (along Z) of an n x n piece."""
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
