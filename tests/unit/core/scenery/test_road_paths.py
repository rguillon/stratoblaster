"""Paths from the main roads to past the screen edge (`core/scenery/road_paths.py`, P04-R07)."""

import math

import pytest
from level_builders import road_rules

from core.math.rng import create_rng
from core.scenery.districts import ZRange
from core.scenery.road_paths import (
    PathGround,
    _find_index,
    _path_line,
    _path_through,
    _path_width,
    _runs_along,
    lay_paths,
)
from core.scenery.road_segments import Nearest
from core.scenery.road_types import Road, RoadPoint
from core.scenery.scenery_level import NoCrossings

SPAN = ZRange(-500.0, 1500.0)


def _main_along_z(x: float = 0.0) -> Road:
    points = [RoadPoint(x, z, 24.0) for z in range(-500, 1501, 10)]
    return Road(0, "main", 24.0, 1, points)


def _ground(rules, laid: list, is_open=lambda x, z: True, nearest=None) -> PathGround:
    def no_road(x: float, z: float, which) -> Nearest:
        return Nearest(math.inf)

    return PathGround(
        rules,
        SPAN,
        is_open,
        nearest if nearest is not None else no_road,
        laid.append,
    )


def test_p04_r07_paths_run_from_the_main_road_past_the_screen_edge() -> None:
    rules = road_rules()
    laid: list = []
    lay_paths(_ground(rules, laid), create_rng(5), [_main_along_z()])
    assert len(laid) > 0
    for path in laid:
        assert path[0].x == 0.0
        assert abs(path[-1].x) >= rules.offscreen_x


def test_p04_r07_paths_are_the_same_for_the_same_seed() -> None:
    def run(seed: int) -> list:
        laid: list = []
        lay_paths(_ground(road_rules(), laid), create_rng(seed), [_main_along_z()])
        return [[(p.x, p.z) for p in path] for path in laid]

    assert run(5) == run(5)
    assert run(5) != run(6)


def test_no_main_road_means_no_path() -> None:
    laid: list = []
    lay_paths(_ground(road_rules(), laid), create_rng(1), [])
    assert laid == []


def test_a_path_that_is_not_on_open_ground_is_dropped() -> None:
    laid: list = []
    lay_paths(
        _ground(road_rules(), laid, is_open=lambda x, z: False), create_rng(5), [_main_along_z()]
    )
    assert laid == []


def test_p04_r07_without_crossings_a_road_running_across_gives_no_paths() -> None:
    rules = road_rules(no_crossings=NoCrossings(20.0))
    across = Road(0, "main", 24.0, 1, [RoadPoint(x, 500.0, 24.0) for x in range(-300, 301, 10)])
    laid: list = []
    lay_paths(_ground(rules, laid), create_rng(5), [across])
    assert laid == []


def test_find_index_is_the_first_point_at_or_past_z_on_screen() -> None:
    points = [RoadPoint(0.0, 0.0, 1.0), RoadPoint(0.0, 50.0, 1.0), RoadPoint(900.0, 60.0, 1.0)]
    assert _find_index(points, 40.0, 300.0) == 1
    assert _find_index(points, 55.0, 300.0) == -1


def test_runs_along_compares_the_run_to_the_turn() -> None:
    along = Road(0, "main", 1.0, 1, [RoadPoint(0.0, 0.0, 1.0), RoadPoint(0.0, 10.0, 1.0)])
    across = Road(1, "main", 1.0, 1, [RoadPoint(0.0, 0.0, 1.0), RoadPoint(10.0, 0.0, 1.0)])
    single = Road(2, "main", 1.0, 1, [RoadPoint(0.0, 0.0, 1.0)])
    assert _runs_along(along, 0) is True
    assert _runs_along(across, 0) is False
    assert _runs_along(across, 1) is False
    assert _runs_along(single, 0) is True
    assert _runs_along(along, 5) is True


def test_path_line_goes_straight_past_the_edge_without_bend() -> None:
    rules = road_rules()
    start = RoadPoint(0.0, 100.0, 24.0)
    line = _path_line(rules, start, 1, 0.0)
    assert line[0].x == 0.0 and line[0].z == 100.0
    assert all(p.z == 100.0 for p in line)
    assert line[-1].x >= rules.offscreen_x
    assert [p.x for p in line] == sorted(p.x for p in line)


def test_path_line_bends_by_its_bend_at_the_far_end() -> None:
    rules = road_rules()
    line = _path_line(rules, RoadPoint(0.0, 100.0, 24.0), -1, 30.0)
    assert line[-1].x <= -rules.offscreen_x
    assert line[-1].z == pytest.approx(130.0)


def test_p04_r07_the_path_widens_at_the_junction() -> None:
    rules = road_rules()
    assert _path_width(rules, 0.0) == rules.junction.width
    assert _path_width(rules, 10 * rules.junction.length_) == rules.cross_width


def test_path_through_gives_up_on_a_line_that_leaves_open_ground() -> None:
    rules = road_rules()
    main = _main_along_z()
    line = [RoadPoint(0.0, 0.0, 12.0), RoadPoint(10.0, 0.0, 12.0), RoadPoint(20.0, 0.0, 12.0)]
    assert _path_through(_ground(rules, []), line, main) == line
    closed = _ground(rules, [], is_open=lambda x, z: x < 15)
    assert _path_through(closed, line, main) is None


def test_p04_r07_without_crossings_a_path_stops_at_a_road_it_runs_into() -> None:
    rules = road_rules(no_crossings=NoCrossings(20.0))
    main = _main_along_z()
    cross = Road(9, "main", 24.0, 1, [])

    def road_ahead(x: float, z: float, which) -> Nearest:
        # The path's own road is far away; a road ahead, at the path's end, is at its edge.
        if which(main):
            return Nearest(math.inf)
        return Nearest(-1.0, cross)

    line = [RoadPoint(0.0, 0.0, 12.0), RoadPoint(10.0, 0.0, 12.0), RoadPoint(20.0, 0.0, 12.0)]
    cut = _path_through(_ground(rules, [], nearest=road_ahead), line, main)
    assert cut == line[0:2]


def test_p04_r07_without_crossings_a_path_going_back_towards_its_road_is_blocked() -> None:
    rules = road_rules(no_crossings=NoCrossings(20.0))
    main = _main_along_z()

    def own_road(x: float, z: float, which) -> Nearest:
        if which(main):
            return Nearest(abs(x) - 5.0, main)
        return Nearest(math.inf)

    # It leaves the road, is clear of it, then comes back towards it: blocked.
    line = [
        RoadPoint(0.0, 0.0, 12.0),
        RoadPoint(10.0, 0.0, 12.0),
        RoadPoint(40.0, 0.0, 12.0),
        RoadPoint(20.0, 0.0, 12.0),
    ]
    assert _path_through(_ground(rules, [], nearest=own_road), line, main) is None


def test_p04_r07_without_crossings_a_path_across_another_road_is_blocked() -> None:
    rules = road_rules(no_crossings=NoCrossings(20.0))
    main = _main_along_z()
    crossing = Road(9, "cross", 12.0, 1, [])

    def other_path(x: float, z: float, which) -> Nearest:
        if which(main):
            return Nearest(math.inf)
        return Nearest(0.5, crossing)

    line = [RoadPoint(0.0, 0.0, 12.0), RoadPoint(10.0, 0.0, 12.0)]
    assert _path_through(_ground(rules, [], nearest=other_path), line, main) is None


def test_p04_r07_without_crossings_a_path_on_closed_ground_is_blocked() -> None:
    rules = road_rules(no_crossings=NoCrossings(20.0))
    line = [RoadPoint(0.0, 0.0, 12.0), RoadPoint(10.0, 0.0, 12.0), RoadPoint(20.0, 0.0, 12.0)]
    closed_at_end = _ground(rules, [], is_open=lambda x, z: x < 15.0)
    assert _path_through(closed_at_end, line, _main_along_z()) is None
