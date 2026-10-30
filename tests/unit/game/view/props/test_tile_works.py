"""Unit tests of `src/game/view/props/tile_works.py`."""

import pytest
from helpers.geometry_checks import check_colored, height

from game.config.tile_buildings import TILE
from game.view.props.tile_kit import geometry_of, tile_kit
from game.view.props.tile_works import (
    build_containers,
    build_cooling_tower,
    build_depot,
    build_dock_crane,
    build_factory,
    build_flare,
    build_foundry,
    build_headframe,
    build_mine_works,
    build_oil_tanks,
    build_ore_silos,
    build_plant,
    build_pumpjack,
    build_radio,
    build_refinery,
    build_solar,
    build_tanks,
    build_warehouse,
    build_water_tower,
)

BUILDERS = [
    build_water_tower,
    build_solar,
    build_radio,
    build_depot,
    build_headframe,
    build_ore_silos,
    build_mine_works,
    build_pumpjack,
    build_oil_tanks,
    build_flare,
    build_refinery,
    build_factory,
    build_warehouse,
    build_containers,
    build_cooling_tower,
    build_tanks,
    build_foundry,
    build_plant,
    build_dock_crane,
]


@pytest.mark.parametrize("builder", BUILDERS, ids=lambda b: b.__name__)
def test_p15_r09_each_works_building_is_a_well_formed_structure_on_the_ground(builder):
    k = tile_kit(30.0, 40.0, TILE.size, 3)
    builder(k)
    prop = geometry_of(k)
    check_colored(prop.structure)
    assert height(prop.structure) > 0


def test_p15_r09_a_flare_stack_is_taller_than_a_solar_array():
    flare = tile_kit(30.0, 40.0, TILE.size, 3)
    build_flare(flare)
    solar = tile_kit(30.0, 40.0, TILE.size, 3)
    build_solar(solar)
    assert height(geometry_of(flare).structure) > height(geometry_of(solar).structure)
