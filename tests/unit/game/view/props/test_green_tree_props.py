"""Unit tests of `src/game/view/props/green_tree_props.py`."""

import pytest
from helpers.geometry_checks import bounds, check_prop, height

from game.view.props.green_tree_props import build_broadleaf_tree, build_bush, build_conifer


@pytest.mark.parametrize("builder", [build_conifer, build_broadleaf_tree, build_bush])
def test_p04_r04_each_green_plant_is_a_well_formed_prop_on_the_ground(builder):
    prop = builder()
    check_prop(prop)
    assert bounds(prop.structure)[0][1] >= 0


def test_p04_r04_a_bush_is_lower_than_a_tree():
    assert height(build_bush().structure) < height(build_conifer().structure)
