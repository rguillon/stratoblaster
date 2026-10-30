"""Unit tests of `src/game/view/props/farm_props.py`."""

import pytest
from helpers.geometry_checks import bounds, check_prop, height

from game.view.props.farm_props import build_farmhouse, build_grain_silos, build_greenhouse


@pytest.mark.parametrize("builder", [build_farmhouse, build_greenhouse, build_grain_silos])
def test_p04_r04_each_farm_building_is_a_well_formed_prop_on_the_ground(builder):
    prop = builder()
    check_prop(prop)
    assert bounds(prop.structure)[0][1] >= 0


def test_p04_r04_the_silos_are_taller_than_the_farmhouse():
    assert height(build_grain_silos().structure) > height(build_farmhouse().structure)
