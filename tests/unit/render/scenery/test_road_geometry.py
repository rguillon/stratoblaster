"""Unit tests of `src/render/scenery/road_geometry.py`."""

from typing import Any

import pytest
from helpers.render_fakes import patch_babylon
from helpers.render_geometry import points_of

from core.scenery.road_types import Road, RoadPoint
from render.geometry.gradient_shapes import ColoredGeometry
from render.scenery import road_geometry
from render.scenery.road_geometry import (
    RoadLook,
    RoadOpacity,
    _across,
    _ribbon_points,
    _runs,
    _worn,
    build_road_geometry,
)

GREY = (0.5, 0.5, 0.5)
RED = (1.0, 0.0, 0.0)


class Flat:
    """Flat ground at height 0."""

    def height(self, x: float, z: float) -> float:
        return 0.0


def _look(**overrides: Any) -> RoadLook:
    values: dict[str, Any] = {
        "main": GREY,
        "cross": RED,
        "opacity": RoadOpacity(0.8, 0.6),
        "shoulder": 1.0,
        "street_shoulder": 0.5,
        "centre_line": None,
        "wear": 0.0,
        "lift": 0.1,
        "tiles": None,
    }
    values.update(overrides)
    return RoadLook(**values)


def _straight(kind: str = "main", z0: float = 0, width: float = 4) -> Road:
    points = [RoadPoint(0, z0 + i * 10, width) for i in range(3)]
    return Road(1, kind, width, 2, points)


def test_runs_split_the_points_at_the_edges_of_the_chunk() -> None:
    points = [RoadPoint(0, z, 1) for z in (0, 5, 10, 15, 20, 25)]
    runs = _runs(points, 4, 16)
    assert [[p.z for p in run] for run in runs] == [[5, 10, 15, 20]]


def test_a_run_is_split_where_the_road_leaves__the_chunk_and_keeps_the_end_that_leaves() -> None:
    # The segment 5 -> 40 starts in the chunk, so its far end (40) is kept, as it is drawn to it.
    points = [RoadPoint(0, z, 1) for z in (0, 5, 40, 45, 10, 15)]
    runs = _runs(points, 0, 20)
    assert [[p.z for p in run] for run in runs] == [[0, 5, 40], [10, 15]]


def test_across_is_a_unit_vector_at_right_angles_to_the_road() -> None:
    run = [RoadPoint(0, 0, 1), RoadPoint(0, 10, 1), RoadPoint(0, 20, 1)]
    nx, nz = _across(run, 1)
    assert (nx, nz) == pytest.approx((1, 0))
    assert nx**2 + nz**2 == pytest.approx(1)


def test_across_of_a_zero_length_step_is_still_a_unit_vector() -> None:
    run = [RoadPoint(0, 0, 1), RoadPoint(0, 0, 1)]
    nx, nz = _across(run, 0)
    assert nx**2 + nz**2 == pytest.approx(1)


def test_a_street_reaches_past_its_end_points_by_half_its_width() -> None:
    street = Road(2, "street", 6, 2, [RoadPoint(0, 0, 6), RoadPoint(0, 10, 6)])
    points = _ribbon_points(street, [])
    assert len(points) == 4
    assert points[0].z == pytest.approx(-3)
    assert points[-1].z == pytest.approx(13)


def test_a_main_road_is_not_extended() -> None:
    main = _straight("main")
    assert _ribbon_points(main, []) == main.points


def test_worn_streets_are_opaque_and_the_others_fade_with_their_opacity() -> None:
    look = _look(wear=0)
    street = _worn(_straight("street"), RoadPoint(0, 0, 4), look)
    assert street == [0.5, 0.5, 0.5, 1]
    main = _worn(_straight("main"), RoadPoint(0, 0, 4), look)
    assert main == pytest.approx([0.5, 0.5, 0.5, 0.8])
    path = _worn(_straight("cross"), RoadPoint(0, 0, 4), look)
    assert path == pytest.approx([1.0, 0.0, 0.0, 0.6])


def test_a_straight_road_is_a_ribbon_of_four_rows_per_point() -> None:
    geo = build_road_geometry([_straight()], Flat(), 0, 100, _look())
    assert len(geo.positions) // 3 == 3 * 4
    # Two segments, three quads each, two triangles per quad.
    assert len(geo.indices) == 2 * 3 * 6


def test_the_ribbon_has_soft_shoulders_on_both_sides() -> None:
    geo = build_road_geometry([_straight()], Flat(), 0, 100, _look(shoulder=1))
    xs = [p[0] for p in points_of(geo.positions)]
    assert min(xs) == pytest.approx(-3)
    assert max(xs) == pytest.approx(3)


def test_the_road_is_lifted_above_the_ground() -> None:
    geo = build_road_geometry([_straight()], Flat(), 0, 100, _look(lift=0.25))
    assert {p[1] for p in points_of(geo.positions)} == {0.25}


def test_the_shoulders_are_transparent_and_the_road_itself_is_not() -> None:
    geo = build_road_geometry([_straight()], Flat(), 0, 100, _look())
    alphas = [geo.colors[i + 3] for i in range(0, 4 * 4, 4)]
    assert alphas == pytest.approx([0, 0.8, 0.8, 0])


def test_a_road_outside_the_chunk_has_no_geometry() -> None:
    geo = build_road_geometry([_straight(z0=500)], Flat(), 0, 100, _look())
    assert geo.positions == []


def test_the_middles_of_streets_go_to_their_own_geometry_opaque() -> None:
    middles = ColoredGeometry()
    geo = build_road_geometry([_straight("street")], Flat(), 0, 100, _look(), middles=middles)
    # The street's ribbon starts 2 units before its first point, which lies outside the chunk:
    # its 3 segments are drawn here. The middle quad of each goes there, the two others stay.
    assert len(middles.indices) == 3 * 6
    assert len(geo.indices) == 3 * 2 * 6


def test_the_centre_line_is_painted_over_the_ribbons(monkeypatch: pytest.MonkeyPatch) -> None:
    painted: list[Any] = []

    def fake_paint(painter: Any, roads: Any, z_min: float, z_max: float) -> None:
        painted.append((roads, z_min, z_max))

    monkeypatch.setattr(road_geometry, "paint_centre_lines", fake_paint)
    roads = [_straight()]
    build_road_geometry(roads, Flat(), 0, 100, _look(centre_line=object()))
    assert painted == [(roads, 0, 100)]


def test_the_geometry_is_a_coloured_geometry() -> None:
    assert isinstance(build_road_geometry([], Flat(), 0, 1, _look()), ColoredGeometry)


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, road_geometry)
    monkeypatch.setattr(road_geometry, "cached_street_lines", lambda roads: [])
    monkeypatch.setattr(road_geometry, "road_z_span", _span)


def _span(road: Road) -> tuple[float, float]:
    zs = [p.z for p in road.points]
    return min(zs), max(zs)
