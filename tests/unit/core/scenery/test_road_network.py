"""Unit tests of `src/core/scenery/road_network.py`."""

import math

import pytest
from helpers.level_builders import (
    SAMPLE_POINTS,
    flat,
    hills,
    make_level,
    road_rules,
    section,
    street_grid,
    tile_rules,
)
from helpers.sample_level import sample_level

from core.scenery.districts import ZRange
from core.scenery.ground_boxes import GroundArea
from core.scenery.height_field import HeightField
from core.scenery.prop_placement import PropPlacer
from core.scenery.road_network import RoadNetwork, RoadNetworkOptions, level_roads
from core.scenery.scenery_level import runout_start, with_runout

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


AREA = GroundArea(-200, 200, 0, 400)


def keys(placements) -> list[tuple]:
    """The placements as plain tuples (PropPlacement has no equality)."""
    return [(p.kind, p.x, p.y, p.z, p.rotation, p.scale) for p in placements]


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


def test_p13_r03_a_snapshot_makes_the_same_placer_without_placing_again() -> None:
    level = sample_level()
    field = HeightField(level, level.seed)
    original = PropPlacer(
        field, level.props, level.seed, level_roads(field, level.roads, level.seed), sea_level=0
    )
    original.ensure_placed(600)
    snapshot = original.snapshot()
    roads = level_roads(
        field,
        level.roads,
        level.seed,
        RoadNetworkOptions(made=original.roads.snapshot()),
    )
    again = PropPlacer(field, level.props, level.seed, roads, sea_level=0, made=snapshot)
    assert again.placed_to == original.placed_to
    assert keys(again.place(AREA)) == keys(original.place(AREA))
