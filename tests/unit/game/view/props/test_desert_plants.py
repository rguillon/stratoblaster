"""Unit tests of `src/game/view/props/desert_plants.py`."""

import pytest
from helpers.geometry_checks import bounds, check_prop, height

from game.view.props.desert_plants import build_cactus, build_dry_bush, build_palm_tree


@pytest.mark.parametrize("builder", [build_palm_tree, build_dry_bush, build_cactus])
def test_p04_r04_each_desert_plant_is_a_well_formed_prop_on_the_ground(builder):
    prop = builder()
    check_prop(prop)
    assert bounds(prop.structure)[0][1] >= -0.25  # roots sink a little into the ground
    assert height(prop.structure) > 0


def test_p04_r04_a_palm_is_taller_than_a_dry_bush():
    assert height(build_palm_tree().structure) > height(build_dry_bush().structure)
