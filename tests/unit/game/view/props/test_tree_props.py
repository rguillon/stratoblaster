"""Unit tests of `src/game/view/props/tree_props.py`."""

import pytest
from helpers.geometry_checks import bounds, check_prop

from game.view.props.tree_props import build_dead_tree, build_forked_tree


@pytest.mark.parametrize("builder", [build_dead_tree, build_forked_tree])
def test_p04_r04_each_bare_tree_is_a_well_formed_prop_on_the_ground(builder):
    prop = builder()
    check_prop(prop)
    assert bounds(prop.structure)[0][1] >= -0.25  # roots sink a little into the ground
