"""Unit tests of `src/core/scenery/road_types.py`."""

import math

from helpers.level_builders import flat, make_level, road_rules, section, street_grid, tile_rules

from core.math.rng import create_rng
from core.scenery.districts import ZRange
from core.scenery.ground_boxes import GroundArea
from core.scenery.height_field import HeightField
from core.scenery.road_network import RoadNetwork, RoadNetworkOptions
from core.scenery.road_paths import (
    PathGround,
    _find_index,
    _path_line,
    _path_through,
    _runs_along,
    lay_paths,
)
from core.scenery.road_segments import Nearest
from core.scenery.road_tiles import road_pieces
from core.scenery.road_traffic import street_lines
from core.scenery.road_types import Road, RoadPoint, RoadSlot, RoadSnapshot
from core.scenery.scenery_level import CarRules, NoCrossings
from core.scenery.traffic import Traffic

SPAN = ZRange(-3000.0, 6000.0)


def _level(terrain=None, streets=True, **rules):
    grid = street_grid(0.55) if streets else None
    secs = [
        section("a", 10, terrain or flat()),
        section("b", 10, terrain or flat(), streets=grid),
        section("c", 10, terrain or flat()),
    ]
    return make_level(secs, roads=road_rules(**rules))


def _network(level, seed: int = 4, options=None) -> RoadNetwork:
    field = HeightField(level)
    return RoadNetwork(field, level.roads, seed, SPAN, options)


def _shape(net: RoadNetwork):
    return [
        (r.index, r.kind, r.width, r.lanes, [(p.x, p.z, p.width) for p in r.points])
        for r in net.roads
    ]


SPAN_PATHS = ZRange(-500.0, 1500.0)


def _main_along_z(x: float = 0.0) -> Road:
    points = [RoadPoint(x, z, 24.0) for z in range(-500, 1501, 10)]
    return Road(0, "main", 24.0, 1, points)


def _ground(rules, laid: list, is_open=lambda x, z: True, nearest=None) -> PathGround:
    def no_road(x: float, z: float, which) -> Nearest:
        return Nearest(math.inf)

    return PathGround(
        rules,
        SPAN_PATHS,
        is_open,
        nearest if nearest is not None else no_road,
        laid.append,
    )


TILE = tile_rules()  # 24 units a side


def _street(index: int, points: list[tuple[float, float]], width: float = 10.0) -> Road:
    return Road(index, "street", width, 1, [RoadPoint(x, z, width) for x, z in points])


FAR = GroundArea(-1000, 1000, -1000, 5000)


def rules(**overrides: object) -> CarRules:
    """One car kind, a car at every point, at 20 units per second."""
    values: dict[str, object] = {
        "kinds": ["car"],
        "density": 1,
        "lift": 0.5,
        "scale": 1,
        "length": 10,
        "speed": [20, 20],
    }
    values.update(overrides)
    return CarRules(**values)  # type: ignore[arg-type]


def ground(x: float, z: float) -> float:
    return 2.0


def test_p13_r03_a_snapshot_restores_the_same_roads_without_making_them_again() -> None:
    level = _level()
    net = _network(level)
    snapshot = net.snapshot()
    assert isinstance(snapshot, RoadSnapshot)
    restored = _network(level, options=RoadNetworkOptions(made=snapshot))
    assert _shape(restored) == _shape(net)
    assert len(restored.slots) == len(net.slots)


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


def test_p04_r07_without_crossings_a_path_on_closed_ground_is_blocked() -> None:
    rules = road_rules(no_crossings=NoCrossings(20.0))
    line = [RoadPoint(0.0, 0.0, 12.0), RoadPoint(10.0, 0.0, 12.0), RoadPoint(20.0, 0.0, 12.0)]
    closed_at_end = _ground(rules, [], is_open=lambda x, z: x < 15.0)
    assert _path_through(closed_at_end, line, _main_along_z()) is None


def test_roads_that_are_not_streets_or_have_no_points_make_no_pieces() -> None:
    main = Road(0, "main", 24.0, 1, [RoadPoint(0.0, 0.0, 24.0), RoadPoint(0.0, 9.0, 24.0)])
    empty = Road(1, "street", 24.0, 1, [])
    assert road_pieces([main, empty], TILE) == []


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


def test_road_keeps_its_points_and_lanes() -> None:
    points = [RoadPoint(0.0, 0.0, 24.0), RoadPoint(0.0, 10.0, 24.0)]
    road = Road(3, "street", 24.0, 1, points)
    assert (road.index, road.kind, road.width, road.lanes) == (3, "street", 24.0, 1)
    assert road.points is points


def test_slot_and_snapshot_hold_what_they_are_given() -> None:
    road = Road(0, "main", 24.0, 1, [])
    slot = RoadSlot(road, 2, 1.0, 2.0, 0.0, -1.0)
    assert (slot.road, slot.index, slot.x, slot.z, slot.nx, slot.nz) == (
        road,
        2,
        1.0,
        2.0,
        0.0,
        -1.0,
    )
    snapshot = RoadSnapshot([road], [], [slot])
    assert snapshot.roads == [road]
    assert snapshot.blocks == []
    assert snapshot.slots == [slot]


def test_a_doubled_point_does_not_break_the_placement() -> None:
    doubled = Road(
        0,
        "main",
        6,
        1,
        [RoadPoint(0, 0, 6), RoadPoint(0, 0, 6), RoadPoint(0, 200, 6), RoadPoint(0, 400, 6)],
    )
    traffic = Traffic([doubled], ground, rules(), 1)
    cars = traffic.at(1.0, FAR)
    assert all(math.isfinite(c.z) for c in cars)


def test_a_road_in_a_bucket_of_the_area_but_not_on_it_is_left_out() -> None:
    near_start = Road(0, "main", 6, 1, [RoadPoint(0, z, 6) for z in range(0, 101, 20)])
    far = Road(1, "main", 6, 1, [RoadPoint(0, z, 6) for z in range(300, 401, 20)])
    traffic = Traffic([near_start, far], ground, rules(), 1)
    cars = traffic.at(0.0, GroundArea(-1000, 1000, 200, 250))
    assert cars == []
