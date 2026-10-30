"""Unit tests of `src/render/scenery/road_lines.py`."""

import pytest
from helpers.render_geometry import babylon_normal, triangles

from core.scenery.road_types import Road, RoadPoint
from render.geometry.gradient_shapes import ColoredGeometry
from render.scenery.road_lines import (
    CentreLineLook,
    Painter,
    _paint_run,
    _quad,
    _straight,
    _stripes,
    paint_centre_lines,
)

GREY = (0.5, 0.5, 0.5)
RED = (1.0, 0.0, 0.0)
WHITE = (1.0, 1.0, 1.0)
LOOK = CentreLineLook(RED, WHITE, 0.5, 4, 0.1)


class Flat:
    """Flat ground at height 0."""

    def height(self, x: float, z: float) -> float:
        return 0.0


class Sloped:
    """Ground that rises along X."""

    def height(self, x: float, z: float) -> float:
        return 0.2 * x


def _road(kind: str, lanes: int, width: float, points: list[tuple[float, float]]) -> Road:
    return Road(1, kind, width, lanes, [RoadPoint(x, z, width) for x, z in points])


def _painter(ground: object = None) -> Painter:
    geo = ColoredGeometry()
    return Painter(geo, ground or Flat(), LOOK, 0.2)  # type: ignore[arg-type]


def test_a_one_lane_road_has_one_centre_stripe_dashed_only_when_it_is_a_main_road() -> None:
    main = _stripes(_road("main", 1, 4, [(0, 0), (0, 10)]), LOOK)
    street = _stripes(_road("street", 1, 4, [(0, 0), (0, 10)]), LOOK)
    assert [(s.offset, s.dashed) for s in main] == [(0, True)]
    assert [(s.offset, s.dashed) for s in street] == [(0, False)]


def test_a_two_lane_road_has_a_double_yellow_line_and_a_dashed_line_between_its_lanes() -> None:
    stripes = _stripes(_road("main", 2, 8, [(0, 0), (0, 10)]), LOOK)
    assert len(stripes) == 4
    solid = [s for s in stripes if not s.dashed]
    dashed = [s for s in stripes if s.dashed]
    assert sorted(s.offset for s in solid) == [-LOOK.width, LOOK.width]
    assert all(s.color == RED for s in solid)
    # Each side has one lane line, a lane (8 / 4 = 2) from the middle.
    assert sorted(s.offset for s in dashed) == [-2, 2]
    assert all(s.color == WHITE for s in dashed)


def test_a_three_lane_road_has_two_lane_lines_on_each_side() -> None:
    stripes = _stripes(_road("main", 3, 12, [(0, 0), (0, 10)]), LOOK)
    assert len(stripes) == 6
    assert sorted(s.offset for s in stripes if s.dashed) == pytest.approx([-4, -2, 2, 4])


def test_a_run_is_straight_while_the_ground_stays_on_the_line_between_its_ends() -> None:
    assert _straight([0.0, 0.34, 0.66, 1.0], 0, 3)
    assert not _straight([0.0, 0.5, 0.0, 1.0], 0, 3)


def test_a_flat_quad_is_a_strip_across_the_road_at_the_lifted_height_facing_up() -> None:
    paint = _painter()
    stripe = _stripes(_road("street", 1, 4, [(0, 0), (10, 0)]), LOOK)[0]
    _quad(paint, stripe, (0, 0), (10, 0), 0, 0)
    geo = paint.geo
    points = [geo.positions[i : i + 3] for i in range(0, len(geo.positions), 3)]
    assert len(points) == 4
    assert all(p[1] == pytest.approx(0.3) for p in points)
    assert sorted({round(p[2], 6) for p in points}) == [-0.25, 0.25]
    assert sorted({round(p[0], 6) for p in points}) == [0, 10]
    tri = triangles(geo.positions, geo.indices)[0]
    assert babylon_normal(tri)[1] > 0


def test_a_run_over_a_straight_slope_is_one_quad() -> None:
    paint = _painter(Sloped())
    stripe = _stripes(_road("street", 1, 4, [(0, 0), (20, 0)]), LOOK)[0]
    at = [(float(x), 0.0) for x in range(0, 21, 2)]
    _paint_run(paint, stripe, at, (1.0, 0.0))
    # The ground rises evenly, so the heights lie on one line and one quad covers the run.
    assert len(paint.geo.indices) // 6 == 1


class Step:
    """Flat ground that steps up at X = 10."""

    def height(self, x: float, z: float) -> float:
        return 0.0 if x < 10 else 1.0


def test_a_run_over_a_step_in_the_ground_is_cut_so_the_quads_follow_it() -> None:
    paint = _painter(Step())
    stripe = _stripes(_road("street", 1, 4, [(0, 0), (20, 0)]), LOOK)[0]
    at = [(float(x), 0.0) for x in range(0, 21, 2)]
    _paint_run(paint, stripe, at, (1.0, 0.0))
    assert len(paint.geo.indices) // 6 > 1


def test_a_main_road_centre_line_is_three_dashes_over_a_20_unit_road() -> None:
    paint = _painter()
    road = _road("main", 1, 8, [(0, 0), (0, 20)])
    paint_centre_lines(paint, [road], 0, 100)
    # Dashes of 4 and gaps of 4 along the road: [0, 4), [8, 12) and [16, 20).
    assert len(paint.geo.indices) // 6 == 3


def test_a_street_centre_line_is_solid_over_the_same_road() -> None:
    paint = _painter()
    road = _road("street", 1, 8, [(0, 0), (0, 20)])
    paint_centre_lines(paint, [road], 0, 100)
    assert len(paint.geo.indices) // 6 == 1


def test_only_the_segments_starting_in_the_range_are_painted() -> None:
    paint = _painter()
    road = _road("street", 1, 8, [(0, 0), (0, 20)])
    paint_centre_lines(paint, [road], 50, 60)
    assert paint.geo.indices == []


def test_a_cross_road_gets_no_centre_line() -> None:
    paint = _painter()
    paint_centre_lines(paint, [_road("cross", 1, 2, [(0, 0), (0, 20)])], 0, 100)
    assert paint.geo.indices == []
