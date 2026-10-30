"""Where streets cross each other or meet (`core/scenery/road_traffic.py`, phase 4 review)."""

import pytest

from core.scenery.road_traffic import (
    StreetIndex,
    StreetLine,
    _distance,
    cached_street_lines,
    in_crossing,
    meeting_width,
    road_z_span,
    street_lines,
)
from core.scenery.road_types import Road, RoadPoint


def _street(index: int, points: list[tuple[float, float]], width: float = 10.0) -> Road:
    return Road(index, "street", width, 1, [RoadPoint(x, z, width) for x, z in points])


def _cross_streets() -> list[StreetLine]:
    """A street along X and one along Z, crossing at the origin."""
    along_x = _street(0, [(-100.0, 0.0), (100.0, 0.0)])
    along_z = _street(1, [(0.0, -100.0), (0.0, 100.0)])
    return street_lines([along_x, along_z])


def test_street_lines_keeps_only_the_straight_streets_with_points() -> None:
    main = Road(5, "main", 24.0, 1, [RoadPoint(0.0, 0.0, 24.0), RoadPoint(0.0, 9.0, 24.0)])
    empty = _street(6, [])
    lines = street_lines([main, empty, _street(7, [(1.0, 2.0), (3.0, 4.0)], width=6.0)])
    assert len(lines) == 1
    line = lines[0]
    assert (line.road, line.ax, line.az, line.bx, line.bz, line.width) == (
        7,
        1.0,
        2.0,
        3.0,
        4.0,
        6.0,
    )


def test_cached_street_lines_are_made_once_per_list() -> None:
    roads = [_street(0, [(0.0, 0.0), (10.0, 0.0)])]
    assert cached_street_lines(roads) is cached_street_lines(roads)
    assert cached_street_lines(list(roads)) is not cached_street_lines(roads)


def test_road_z_span_is_the_lowest_and_highest_z() -> None:
    assert road_z_span(_street(0, [(0.0, 5.0), (0.0, -3.0), (4.0, 12.0)])) == (-3.0, 12.0)


def test_distance_to_a_street_and_to_a_degenerate_one() -> None:
    line = StreetLine(0, 0.0, 0.0, 10.0, 0.0, 4.0)
    assert _distance(line, 5.0, 3.0) == pytest.approx(3.0)
    point = StreetLine(0, 3.0, 0.0, 3.0, 0.0, 4.0)
    assert _distance(point, 0.0, 4.0) == pytest.approx(5.0)


def test_street_index_finds_the_streets_of_a_band_of_z() -> None:
    near = StreetLine(0, 0.0, 10.0, 0.0, 60.0, 10.0)
    far = StreetLine(1, 0.0, 900.0, 0.0, 950.0, 10.0)
    index = StreetIndex([near, far])
    assert near in index.near(40.0)
    assert far not in index.near(40.0)
    assert list(index.near(5000.0)) == []


def test_p04_r07_a_street_crosses_a_street_it_runs_into() -> None:
    lines = _cross_streets()
    assert in_crossing(lines, 0, 0.0, 0.0, 0.0)
    assert not in_crossing(lines, 0, 50.0, 30.0, 0.0)
    # A wide margin looks past the bands: the street across is still found.
    assert in_crossing(lines, 0, 50.0, 30.0, 60.0)
    assert not in_crossing(lines, 0, 50.0, 30.0, 10.0)


def test_p04_r07_in_crossing_ignores_the_street_itself() -> None:
    lines = street_lines([_street(0, [(-100.0, 0.0), (100.0, 0.0)])])
    assert not in_crossing(lines, 0, 0.0, 0.0, 0.0)


def test_meeting_width_is_the_widest_street_met_or_none() -> None:
    lines = street_lines(
        [
            _street(0, [(-100.0, 0.0), (100.0, 0.0)], width=10.0),
            _street(1, [(0.0, -100.0), (0.0, 100.0)], width=30.0),
        ]
    )
    assert meeting_width(lines, 0, 0.0, 0.0) == 30.0
    assert meeting_width(lines, 0, 50.0, 0.0) is None


def test_the_index_is_rebuilt_for_other_lines() -> None:
    first = street_lines([_street(0, [(0.0, 0.0), (100.0, 0.0)])])
    second = street_lines(
        [_street(0, [(0.0, 0.0), (0.0, 100.0)]), _street(1, [(5.0, 0.0), (5.0, 9.0)])]
    )
    assert in_crossing(first, 0, 50.0, 0.0, 0.0) is False
    assert in_crossing(second, 0, 0.0, 50.0, 0.0) is False
    assert in_crossing(second, 1, 2.0, 2.0, 0.0) is True
