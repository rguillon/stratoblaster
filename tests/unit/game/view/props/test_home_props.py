"""Unit tests of `src/game/view/props/home_props.py`."""

import pytest
from helpers.geometry_checks import bounds, check_prop

from game.view.props.home_props import build_cube_home, build_dome_home


@pytest.mark.parametrize("builder", [build_cube_home, build_dome_home])
def test_p04_r04_each_home_is_a_well_formed_prop_on_the_ground(builder):
    prop = builder()
    check_prop(prop)
    assert bounds(prop.structure)[0][1] >= 0
