"""Unit tests of `src/game/view/props/city_lots.py`."""

import pytest
from helpers.geometry_checks import bounds, check_colored, height

from game.config.tile_buildings import TILE
from game.view.props.city_lots import (
    courtyard,
    crown,
    l_block,
    plinth,
    round_tower,
    slab,
    stepped_tower,
    volume,
)
from game.view.props.tile_city import lot_kit
from game.view.props.tile_kit import geometry_of, tile_kit

FACADES = [[0.6, 0.6, 0.6]]
LIGHTS = [[1.0, 0.9, 0.5]]
LOT = [0.0, 0.0, 16.0, 16.0]


def kit_for(seed=2):
    k = tile_kit(16.0, 16.0, TILE.size, seed)
    return k, lot_kit(k, FACADES, LIGHTS)


def test_p15_r08_a_volume_is_a_box_up_to_its_height():
    k, kit = kit_for()
    volume(kit, LOT, 0.0, 12.0)
    prop = geometry_of(k)
    check_colored(prop.structure)
    low, high = bounds(prop.structure)
    assert high[1] == pytest.approx(12.0)
    assert low[1] == pytest.approx(0.0)


def test_p15_r08_a_low_volume_gets_no_window_rows():
    k, kit = kit_for()
    volume(kit, LOT, 0.0, 4.0)
    assert geometry_of(k).lights is not None
    assert len(geometry_of(k).lights.positions) == 0


def test_p15_r08_a_tall_volume_gets_window_rows():
    k, kit = kit_for()
    volume(kit, LOT, 0.0, 20.0)
    assert len(geometry_of(k).lights.positions) > 0


def test_p15_r08_the_plinth_covers_the_lot_and_returns_its_height():
    k, kit = kit_for()
    base = plinth(kit, LOT)
    assert 3 <= base <= 6
    assert height(geometry_of(k).structure) == pytest.approx(base)


@pytest.mark.parametrize("shape", [stepped_tower, round_tower, slab, courtyard, l_block])
def test_p15_r08_each_lot_shape_is_a_well_formed_volume(shape):
    k, kit = kit_for()
    shape(kit, LOT)
    check_colored(geometry_of(k).structure)
    assert height(geometry_of(k).structure) > 0


def test_p15_r08_a_crown_sits_on_the_roof_at_the_given_point():
    k, kit = kit_for()
    # The point is (x, y, z): the crown stands at the top of its tower.
    crown(kit, [8.0, 12.0, 8.0], 2.0)
    check_colored(geometry_of(k).structure)
    _, high = bounds(geometry_of(k).structure)
    assert high[1] >= 12.0
