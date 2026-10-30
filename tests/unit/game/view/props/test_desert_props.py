"""Unit tests of `src/game/view/props/desert_props.py`."""

import pytest
from helpers.geometry_checks import bounds, check_prop

from game.view.props.desert_props import build_beach_hut, build_desert_home


@pytest.mark.parametrize("builder", [build_desert_home, build_beach_hut])
def test_p04_r04_each_desert_building_is_a_well_formed_prop_on_the_ground(builder):
    prop = builder()
    check_prop(prop)
    assert bounds(prop.structure)[0][1] >= 0
