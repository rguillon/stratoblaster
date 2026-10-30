"""Unit tests of `src/core/scenery/road_paths.py`."""

import math

import pytest
from helpers.level_builders import road_rules

from core.math.rng import create_rng
from core.scenery.districts import ZRange
from core.scenery.road_paths import PathGround, _path_line, _path_width, lay_paths
from core.scenery.road_segments import Nearest
from core.scenery.road_types import Road, RoadPoint

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


def test_path_line_bends_by_its_bend_at_the_far_end() -> None:
    rules = road_rules()
    line = _path_line(rules, RoadPoint(0.0, 100.0, 24.0), -1, 30.0)
    assert line[-1].x <= -rules.offscreen_x
    assert line[-1].z == pytest.approx(130.0)


def test_p04_r07_the_path_widens_at_the_junction() -> None:
    rules = road_rules()
    assert _path_width(rules, 0.0) == rules.junction.width
    assert _path_width(rules, 10 * rules.junction.length_) == rules.cross_width
