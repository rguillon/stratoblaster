"""Segments of the roads, their buckets and the building slots along them (`road_segments.py`)."""

import math

import pytest

from core.scenery.road_segments import SegmentIndex, add_slots, segment_distance
from core.scenery.road_types import Road, RoadPoint


def _road(index: int, points: list[tuple[float, float]], width: float = 10.0, kind: str = "main"):
    return Road(index, kind, width, 1, [RoadPoint(x, z, width) for x, z in points])


def test_segment_distance_is_to_the_nearest_point_of_the_segment() -> None:
    from core.scenery.road_segments import Segment  # noqa: PLC0415 (keeps the import near its use)

    s = Segment(None, 0.0, 0.0, 10.0, 0.0, 0.0)  # type: ignore[arg-type]
    assert segment_distance(5.0, 3.0, s) == pytest.approx(3.0)
    assert segment_distance(-4.0, 0.0, s) == pytest.approx(4.0)
    assert segment_distance(13.0, 4.0, s) == pytest.approx(5.0)
    degenerate = Segment(None, 2.0, 2.0, 2.0, 2.0, 0.0)  # type: ignore[arg-type]
    assert segment_distance(5.0, 6.0, degenerate) == pytest.approx(5.0)


def test_p04_r07_nearest_reports_the_edge_of_the_road() -> None:
    index = SegmentIndex()
    road = _road(0, [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)])
    index.add(road)
    on_centre = index.nearest(50.0, 0.0, lambda r: True)
    assert on_centre.distance == pytest.approx(-5.0)
    assert on_centre.road is road
    assert index.nearest(50.0, 20.0, lambda r: True).distance == pytest.approx(15.0)


def test_nearest_skips_the_roads_not_accepted() -> None:
    index = SegmentIndex()
    index.add(_road(0, [(0.0, 0.0), (100.0, 0.0)]))
    nearest = index.nearest(50.0, 20.0, lambda r: False)
    assert nearest.distance == math.inf
    assert nearest.road is None


def test_nearest_is_infinite_with_no_road_near() -> None:
    index = SegmentIndex()
    index.add(_road(0, [(0.0, 0.0), (10.0, 0.0)]))
    assert index.nearest(5000.0, 5000.0, lambda r: True).distance == math.inf


def test_a_single_point_road_has_no_segment() -> None:
    index = SegmentIndex()
    index.add(_road(0, [(0.0, 0.0)]))
    assert index.nearest(0.0, 0.0, lambda r: True).distance == math.inf


def test_p04_r07_clear_of_agrees_with_the_nearest_road() -> None:
    index = SegmentIndex()
    index.add(_road(0, [(0.0, 0.0), (120.0, 0.0), (120.0, 90.0)], width=16.0))
    index.add(_road(1, [(-40.0, 150.0), (60.0, 150.0)], width=8.0))
    for clearance in (2.0, 10.0, 40.0, 100.0):
        for x in range(-80, 200, 17):
            for z in range(-60, 220, 19):
                expected = index.nearest(float(x), float(z), lambda r: True).distance >= clearance
                assert index.clear_of(float(x), float(z), clearance) == expected


def test_add_slots_places_them_every_spacing_on_both_sides() -> None:
    slots: list = []
    add_slots(_road(0, [(0.0, 0.0), (0.0, 100.0)], kind="street"), 20.0, slots)
    assert [round(s.z) for s in slots[::2]] == [10, 30, 50, 70, 90]
    assert {round(s.nx) for s in slots} == {1, -1}
    assert all(s.nz == pytest.approx(0.0) for s in slots)
    assert [s.index for s in slots] == list(range(10))


def test_add_slots_carries_on_across_points_and_skips_repeats() -> None:
    plain: list = []
    add_slots(_road(0, [(0.0, 0.0), (0.0, 100.0)]), 20.0, plain)
    split: list = []
    add_slots(_road(0, [(0.0, 0.0), (0.0, 30.0), (0.0, 30.0), (0.0, 100.0)]), 20.0, split)
    assert [s.z for s in split] == pytest.approx([s.z for s in plain])
