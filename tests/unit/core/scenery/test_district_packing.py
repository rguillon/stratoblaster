"""Buildings of whole tiles in the districts' blocks (P15-R07, R08; `district_packing.py`)."""

from level_builders import (
    flat,
    make_level,
    prop_rules,
    road_rules,
    section,
    street_grid,
    tile_rules,
)

from core.scenery.district_packing import DistrictSite, RoadTilesCache, pack_districts
from core.scenery.districts import ZRange
from core.scenery.height_field import HeightField
from core.scenery.road_network import RoadNetwork
from core.scenery.road_tiles import tile_has
from core.scenery.scenery_level import PropGroupRule, PropKindRule

SPAN = ZRange(-3000.0, 6000.0)
TILE = tile_rules()
ONE = PropKindRule("one", 1.0, 12.0, (0.5, 1.0), tiles=(1, 1))
TWO = PropKindRule("two", 1.0, 24.0, (0.5, 1.0), tiles=(2, 2))
LOT = PropKindRule("lot", 1.0, 12.0, (0.5, 1.0), tiles=(3, 1))


def _setup(group_at=None, lots=(LOT,), seed: int = 4):
    level = make_level(
        [
            section("a", 10, flat()),
            section("b", 10, flat(), streets=street_grid(0.8), building_density=1.0),
            section("c", 10, flat()),
        ],
        roads=road_rules(tiles=TILE),
        props=prop_rules(lots=list(lots)),
    )
    field = HeightField(level)
    roads = RoadNetwork(field, level.roads, seed, SPAN)
    group = PropGroupRule("g", 1.0, [ONE, TWO])
    placed: list = []
    site = DistrictSite(
        field,
        level.props,
        roads,
        seed,
        group_at if group_at is not None else (lambda x, z, section: group),
        placed.append,
    )
    return site, roads, placed


def _footprint_tiles(building) -> set[tuple[int, int]]:
    t = TILE.size
    p = building.placement
    i0 = round((p.x - building.half_x) / t)
    i1 = round((p.x + building.half_x) / t)
    j0 = round((p.z - building.half_z) / t)
    j1 = round((p.z + building.half_z) / t)
    return {(i, j) for i in range(i0, i1) for j in range(j0, j1)}


def _pack(site, roads, within=lambda z: True):
    road = RoadTilesCache().of(roads.roads, TILE)
    pack_districts(site, within, TILE, road)
    return road


def test_p15_r07_buildings_stand_on_whole_tiles_off_the_roads_and_apart() -> None:
    site, roads, placed = _setup()
    road = _pack(site, roads)
    assert placed
    seen: set[tuple[int, int]] = set()
    for building in placed:
        tiles = _footprint_tiles(building)
        assert tiles
        assert not any(tile_has(road, i, j) for i, j in tiles)
        assert not (tiles & seen)
        seen |= tiles


def test_p15_r08_buildings_are_the_same_for_the_same_seed() -> None:
    def placements(seed: int):
        site, roads, placed = _setup(seed=seed)
        _pack(site, roads)
        return [(b.placement.kind, b.placement.x, b.placement.z) for b in placed]

    assert placements(4) == placements(4)


def test_p15_r07_no_buildings_outside_the_places_asked_for() -> None:
    site, roads, placed = _setup()
    _pack(site, roads, within=lambda z: False)
    assert placed == []


def test_p15_r08_where_no_building_fits_the_lots_are_used() -> None:
    site, roads, placed = _setup(group_at=lambda x, z, section: None)
    _pack(site, roads)
    assert placed
    assert {b.placement.kind for b in placed} == {"lot"}


def test_p15_r08_a_group_without_tile_kinds_leaves_the_lots() -> None:
    empty = PropGroupRule("empty", 1.0, [])
    site, roads, placed = _setup(group_at=lambda x, z, section: empty)
    _pack(site, roads)
    assert {b.placement.kind for b in placed} == {"lot"}


def test_p15_r08_a_group_with_no_lots_leaves_the_ground_empty_where_nothing_fits() -> None:
    site, roads, placed = _setup(group_at=lambda x, z, section: None, lots=())
    _pack(site, roads)
    assert placed == []


def test_p15_r07_the_road_tiles_are_worked_out_once_per_list_of_roads() -> None:
    site, roads, _ = _setup()
    cache = RoadTilesCache()
    first = cache.of(roads.roads, TILE)
    assert cache.of(roads.roads, TILE) is first
    assert cache.of(list(roads.roads), TILE) is not first


def test_p15_r08_areas_of_different_groups_pack_with_their_own_kinds() -> None:
    other = PropGroupRule("other", 1.0, [ONE])
    group = PropGroupRule("g", 1.0, [TWO])
    site, roads, placed = _setup(group_at=lambda x, z, section: group if x < 0.0 else other)
    _pack(site, roads)
    assert placed
    kinds = {b.placement.kind for b in placed}
    assert kinds <= {"one", "two", "lot"}
    assert {"one", "two"} <= kinds
