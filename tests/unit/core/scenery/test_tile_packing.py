"""Unit tests of `src/core/scenery/tile_packing.py`."""

import math

import pytest
from helpers.level_builders import flat, hills, make_level, prop_rules, section, tile_rules

from core.scenery.height_field import HeightField
from core.scenery.scenery_level import PropKindRule
from core.scenery.tile_packing import (
    FACINGS,
    PackSite,
    TileBlock,
    TileGround,
    TileSpot,
    _away_from_roads,
    _corners_at,
    _faces,
    _free_tiles,
    _room_for,
    _run,
    _spot_at,
    _spot_for,
    _turn_of,
    pack_block,
)

BLOCK = TileBlock(0, 6, 0, 6)

ONE = PropKindRule("one", 1.0, 1.0, (0.5, 1.0), tiles=(1, 1))

TWO = PropKindRule("two", 1.0, 2.0, (0.5, 1.0), tiles=(2, 2))


def _site(free=None, road=None, kinds=(ONE,), random=lambda k: 0.3) -> PackSite:
    def is_free(x: int, z: int) -> bool:
        return True if free is None else free(x, z)

    def is_road(x: int, z: int) -> bool:
        return False if road is None else road(x, z)

    return PackSite(is_free, is_road, lambda x, z, n: list(kinds), random)


def test_p15_r08_a_block_is_packed_to_about_its_density() -> None:
    spots: list[TileSpot] = []
    pack_block(_site(), BLOCK, 0.5, spots.append)
    covered = [(s.x, s.z) for s in spots]
    assert len(covered) == len(set(covered)) == 18
    assert all(BLOCK.x0 <= x < BLOCK.x1 and BLOCK.z0 <= z < BLOCK.z1 for x, z in covered)


def test_p15_r08_only_free_tiles_are_built_on() -> None:
    spots: list[TileSpot] = []
    pack_block(_site(free=lambda x, z: x < 2), BLOCK, 1.0, spots.append)
    assert spots
    assert all(s.x < 2 for s in spots)


def test_p15_r08_packing_is_the_same_for_the_same_draws() -> None:
    def pack() -> list[tuple[int, int]]:
        spots: list[TileSpot] = []
        pack_block(_site(random=lambda k: (k * 0.37) % 1.0), BLOCK, 0.6, spots.append)
        return [(s.x, s.z) for s in spots]

    assert pack() == pack()


def test_p15_r08_a_spot_turns_to_face_the_road_beside_it() -> None:
    # A road along the -X side of tile column 0 (outside the block): the spot faces it.
    site = _site(road=lambda x, z: x == -1)
    spot = _spot_for(site, BLOCK, ONE, 0, 2, 0.3, (6, 6))
    assert spot is not None
    assert spot.rotation == pytest.approx(math.pi / 2)


def test_p15_r08_without_a_road_the_spot_turns_by_its_draw() -> None:
    site = _site()
    assert _spot_for(site, BLOCK, ONE, 2, 2, 0.3, (6, 6)).rotation == pytest.approx(0.0)
    assert _spot_for(site, BLOCK, ONE, 2, 2, 0.7, (6, 6)).rotation == pytest.approx(math.pi)


def test_p15_r08_no_spot_where_the_room_or_the_tiles_do_not_allow() -> None:
    assert _spot_for(_site(), BLOCK, ONE, 2, 2, 0.3, (0, 0)) is None
    assert _spot_for(_site(free=lambda x, z: False), BLOCK, ONE, 2, 2, 0.3, (6, 6)) is None


def test_p15_r08_a_big_kind_is_not_put_over_the_left_tiles() -> None:
    site = _site(kinds=(TWO,))
    assert _spot_at(site, BLOCK, 2, 2, 0, 0.5, first=False) is None
    assert _spot_at(site, BLOCK, 2, 2, 0, 0.5, first=True) is not None


def test_p15_r08_faces_and_away_from_roads() -> None:
    site = _site(road=lambda x, z: z == 1)
    assert _faces(site, 0, 2, 1, 1, FACINGS[0]) is True
    assert _faces(site, 0, 2, 1, 1, FACINGS[1]) is False
    assert _away_from_roads(site, 0, 2, 1, 1) is False
    assert _away_from_roads(_site(), 0, 2, 1, 1) is True


def test_helpers_of_the_packing() -> None:
    assert _turn_of(0.2, FACINGS[2]) == FACINGS[2][2]
    assert _turn_of(0.8, FACINGS[2]) == pytest.approx(FACINGS[2][2] + math.pi)
    assert _room_for(2, 2, 2, 2) is True
    assert _room_for(2, 3, 2, 2) is False
    assert _corners_at(5, 5, 2, 2) == [(5, 5), (4, 5), (5, 4), (4, 4)]
    assert _run(_site(), BLOCK, 0, 0, 1, 0) == 6
    assert sorted(_free_tiles(_site(free=lambda x, z: x == 0 and z < 2), BLOCK)) == [(0, 0), (0, 1)]


def test_tile_ground_fit_follows_the_height_and_slope_limits() -> None:
    flat_field = HeightField(make_level([section("a", 10, flat(10))]))
    rules = prop_rules(min_height=5.0, max_slope=0.5)
    ground = TileGround(flat_field, tile_rules(), rules)
    assert ground.fit(0, 0) is True
    assert TileGround(flat_field, tile_rules(), prop_rules(min_height=20.0)).fit(0, 0) is False
    rough = HeightField(make_level([section("a", 10, hills())]))
    steep = TileGround(rough, tile_rules(), prop_rules(max_slope=1e-6))
    tiles = [(x, z) for x in range(-5, 5) for z in range(-5, 5)]
    assert not any(steep.fit(x, z) for x, z in tiles)
    loose = TileGround(rough, tile_rules(), prop_rules(max_slope=1e6))
    assert all(loose.fit(x, z) for x, z in tiles)


def test_p15_r08_a_spot_stands_at_the_lowest_ground_under_it() -> None:
    rough = HeightField(make_level([section("a", 10, hills())]))
    ground = TileGround(rough, tile_rules(), prop_rules())
    spot = TileSpot(ONE, 3, 4, 2, 2, 0.0)
    corners = [rough.height(i * 24.0, j * 24.0) for i in range(3, 6) for j in range(4, 7)]
    assert ground.lowest(spot) == pytest.approx(min(corners))
