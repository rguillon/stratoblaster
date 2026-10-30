"""Randomly generated roads and paths of a level (P04-R07, P13-R03, P15-R03; `road_network.py`)."""

import math

import pytest
from level_builders import (
    SAMPLE_POINTS,
    flat,
    hills,
    make_level,
    road_rules,
    section,
    street_grid,
    tile_rules,
)

from core.scenery.districts import ZRange
from core.scenery.height_field import HeightField
from core.scenery.road_network import (
    RoadNetwork,
    RoadNetworkOptions,
    level_roads,
)
from core.scenery.road_types import RoadSnapshot
from core.scenery.scenery_level import Boulevard, NoCrossings, runout_start, with_runout

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


def _mains(net):
    return [r for r in net.roads if r.kind == "main"]


def test_p04_r07_the_roads_are_the_same_for_the_same_seed() -> None:
    level = _level()
    assert _shape(_network(level, 4)) == _shape(_network(level, 4))
    assert _shape(_network(level, 4)) != _shape(_network(level, 5))


def test_p04_r07_there_are_the_main_roads_asked_for_and_they_wind() -> None:
    net = _network(_level(streets=False))
    mains = _mains(net)
    assert len(mains) == road_rules().main_roads
    assert all(len(r.points) > 10 for r in mains)
    assert len({round(p.x, 3) for p in mains[0].points}) > 5


def test_p04_r07_main_roads_start_and_end_off_the_screen() -> None:
    rules = road_rules()
    net = _network(_level(streets=False))
    for road in _mains(net):
        for p in (road.points[0], road.points[-1]):
            off = (
                abs(p.x) >= rules.offscreen_x or p.z <= SPAN.z_min or p.z >= SPAN.z_max - rules.step
            )
            assert off


def test_p04_r07_paths_run_past_the_screen_edge() -> None:
    rules = road_rules()
    net = _network(_level(streets=False))
    paths = [r for r in net.roads if r.kind == "cross"]
    assert paths
    assert all(abs(r.points[-1].x) >= rules.offscreen_x for r in paths)


def test_p04_r07_every_point_of_a_winding_road_is_on_buildable_ground() -> None:
    terrain = hills(50.0, 30.0)
    rules = dict(min_height=30.0, max_slope=0.6)
    net = _network(_level(terrain=terrain, streets=False, **rules))
    for road in net.roads:
        if road.kind == "street":
            continue
        assert all(net.buildable(p.x, p.z) for p in road.points)


def test_p04_r07_no_ground_that_cannot_hold_a_road_means_no_roads() -> None:
    net = _network(_level(streets=False, min_height=1e6))
    assert net.roads == []
    assert net.slots == []


def test_p04_r07_roads_are_flagged_and_sized_by_their_lanes() -> None:
    rules = road_rules()
    net = _network(_level())
    for road in net.roads:
        if road.kind != "street":
            assert road.lanes == (2 if road.width >= rules.dual.width else 1)


def test_p04_r07_slots_sit_on_their_road_at_unit_normals() -> None:
    net = _network(_level(streets=False))
    assert net.slots
    for slot in net.slots:
        assert slot.nx**2 + slot.nz**2 == pytest.approx(1.0)
        distance = net.edge_distance(slot.x, slot.z, except_road=None)
        assert distance <= 0.0 + 1e-9


def test_p04_r07_edge_distance_is_negative_on_a_road() -> None:
    net = _network(_level(streets=False))
    road = _mains(net)[0]
    p = road.points[len(road.points) // 2]
    assert net.edge_distance(p.x, p.z) < 0.0
    # Leaving one road out can only make the nearest edge farther.
    assert net.edge_distance(p.x, p.z, except_road=road) >= net.edge_distance(p.x, p.z)


def test_p04_r07_clear_of_agrees_with_the_edge_distance() -> None:
    net = _network(_level(streets=False))
    for x, z in SAMPLE_POINTS:
        for clearance in (1.0, 20.0, 80.0):
            assert net.clear_of(x, z, clearance) == (net.edge_distance(x, z) >= clearance)


def test_p13_r03_a_snapshot_restores_the_same_roads_without_making_them_again() -> None:
    level = _level()
    net = _network(level)
    snapshot = net.snapshot()
    assert isinstance(snapshot, RoadSnapshot)
    restored = _network(level, options=RoadNetworkOptions(made=snapshot))
    assert _shape(restored) == _shape(net)
    assert len(restored.slots) == len(net.slots)


def test_p04_r07_without_crossings_each_main_road_keeps_its_gap_from_the_ones_before() -> None:
    gap = 20.0
    net = _network(_level(streets=False, no_crossings=NoCrossings(gap), main_roads=3))
    mains = _mains(net)
    assert len(mains) >= 2
    for k in range(1, len(mains)):
        for p in mains[k].points:
            for j in range(k):
                edge = _distance_to_road(p.x, p.z, mains[j]) - mains[j].width / 2
                assert edge >= mains[k].width / 2 + gap - 1e-6


def _distance_to_road(x: float, z: float, road) -> float:
    best = math.inf
    for a, b in zip(road.points, road.points[1:], strict=False):
        dx = b.x - a.x
        dz = b.z - a.z
        n = dx * dx + dz * dz
        t = 0.0 if n == 0 else max(0.0, min(1.0, ((x - a.x) * dx + (z - a.z) * dz) / n))
        best = min(best, math.hypot(a.x + t * dx - x, a.z + t * dz - z))
    return best


def test_p15_r03_on_tiles_streets_have_lanes_by_their_tile_width_and_no_slots() -> None:
    level = make_level(
        [
            section("a", 10, flat()),
            section("b", 10, flat(), streets=street_grid(0.7)),
            section("c", 10, flat()),
        ],
        roads=road_rules(tiles=tile_rules()),
    )
    net = _network(level)
    streets = [r for r in net.roads if r.kind == "street"]
    assert streets
    for road in streets:
        assert road.lanes == max(1, min(4, math.floor(road.width / 24.0 + 0.5)))
    assert all(slot.road.kind != "street" for slot in net.slots)
    assert net.tiles is not None


def test_p04_r07_boulevards_have_their_lanes() -> None:
    level = _level(boulevards=[Boulevard(3, 36.0, 0.5)])
    net = _network(level)
    assert any(r.width == 36.0 and r.lanes == 3 for r in net.roads if r.kind == "street")


def test_p04_r07_a_level_roads_span_runs_past_both_ends_of_the_level() -> None:
    level = _level(streets=False)
    net = level_roads(HeightField(level), level.roads, 4)
    assert net.range.z_min == -3000.0
    assert net.range.z_max == pytest.approx(HeightField(level).length_ + 3000.0)
    assert net.blocks is not None


def test_p04_r07_the_runout_is_laid_once_and_can_be_made_elsewhere() -> None:
    # Streets in the last section too, so the runout has streets of its own to lay.
    level = with_runout(
        make_level(
            [
                section("a", 10, flat()),
                section("b", 10, flat(), streets=street_grid(0.55)),
                section("c", 10, flat(), streets=street_grid(0.55)),
            ],
            roads=road_rules(),
        ),
        15.0,
    )
    field = HeightField(level)
    options = RoadNetworkOptions(runout_from=runout_start(level))
    net = RoadNetwork(field, level.roads, 4, SPAN, options)
    assert net.runout_laid is False
    added = net.add_runout()
    assert net.runout_laid is True
    assert len(net.roads) >= len(added.roads)
    again = net.add_runout()
    assert again.roads == [] and again.slots == []

    other = RoadNetwork(field, level.roads, 4, SPAN, options)
    twin = other.add_runout(made=added)
    assert [r.points for r in twin.roads] == [r.points for r in added.roads]
    assert len(other.roads) == len(net.roads)


def test_p04_r07_blocks_of_the_districts_have_room() -> None:
    net = _network(_level())
    assert net.blocks
    assert all(b.x_max > b.x_min and b.z_max > b.z_min for b in net.blocks)
