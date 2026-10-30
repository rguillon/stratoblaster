"""Unit tests of `src/game/view/props/tile_towers.py`."""

import pytest
from helpers.geometry_checks import check_colored, height

from game.config.tile_buildings import TILE
from game.view.props.tile_city import lot_kit
from game.view.props.tile_kit import geometry_of, tile_kit
from game.view.props.tile_towers import SILHOUETTES, Tower, asymmetry, city_building

FACADES = [[0.6, 0.6, 0.6]]
LIGHTS = [[1.0, 0.9, 0.5]]


def tower_of(seed=2):
    """A tower on a 20 x 20 plot, its plinth at 0 and its top at 30."""
    k = tile_kit(20.0, 20.0, TILE.size, seed)
    return k, Tower(k, lot_kit(k, FACADES, LIGHTS), 0.0, 30.0)


@pytest.mark.parametrize("shape", SILHOUETTES, ids=[s.__name__ for s in SILHOUETTES])
def test_p15_r09_each_silhouette_is_a_well_formed_tower_up_to_its_top(shape):
    k, tower = tower_of()
    shape(tower)
    prop = geometry_of(k)
    check_colored(prop.structure)
    assert height(prop.structure) > 0


@pytest.mark.parametrize("seed", range(1, 9))
def test_p15_r09_a_city_building_is_built_on_its_plot_by_its_seed(seed):
    k = tile_kit(20.0, 20.0, TILE.size, seed)
    city_building(k, lot_kit(k, FACADES, LIGHTS), [25.0, 40.0])
    prop = geometry_of(k)
    check_colored(prop.structure)
    assert height(prop.structure) > 0


def test_p15_r09_an_asymmetric_tower_adds_an_annex_to_the_plain_one():
    k, tower = tower_of(seed=5)
    asymmetry(tower)
    assert height(geometry_of(k).structure) > 0
