"""Unit tests of `src/game/view/props/tile_homes.py`."""

import pytest
from helpers.geometry_checks import bounds, check_colored, height

from game.config.tile_buildings import TILE
from game.view.props.tile_homes import (
    build_adobe,
    build_barn,
    build_cottage,
    build_courtyard,
    build_farmhouse,
    build_flats,
    build_greenhouse,
    build_house,
    build_shed,
    build_terrace,
    build_villa,
    build_workshop,
)
from game.view.props.tile_kit import geometry_of, tile_kit

BUILDERS = [
    build_house,
    build_villa,
    build_cottage,
    build_terrace,
    build_flats,
    build_workshop,
    build_farmhouse,
    build_barn,
    build_greenhouse,
    build_adobe,
    build_courtyard,
]


@pytest.mark.parametrize("builder", BUILDERS, ids=lambda b: b.__name__)
@pytest.mark.parametrize("seed", [1, 2])
def test_p15_r09_each_home_is_a_well_formed_building_on_the_ground(builder, seed):
    k = tile_kit(20.0, 20.0, TILE.size, seed)
    builder(k)
    prop = geometry_of(k)
    check_colored(prop.structure)
    assert height(prop.structure) > 0


def test_p15_r09_a_shed_is_a_red_box_of_its_size_at_its_place():
    k = tile_kit(20.0, 20.0, TILE.size, 1)
    build_shed(k, [2.0, -3.0], [4.0, 6.0])
    low, high = bounds(geometry_of(k).structure)
    assert low[1] == pytest.approx(0)
    # Walls of 5 under a gable roof above them.
    assert high[1] > 5
    assert high[0] - low[0] == pytest.approx(4.0)
    assert high[2] - low[2] == pytest.approx(6.0)


def test_p15_r09_flats_stand_taller_than_a_cottage():
    flats = tile_kit(20.0, 20.0, TILE.size, 1)
    build_flats(flats)
    cottage = tile_kit(20.0, 20.0, TILE.size, 1)
    build_cottage(cottage)
    assert height(geometry_of(flats).structure) > height(geometry_of(cottage).structure)
