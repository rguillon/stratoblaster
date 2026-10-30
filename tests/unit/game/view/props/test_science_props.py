"""Unit tests of `src/game/view/props/science_props.py`."""

from helpers.geometry_checks import bounds, check_prop, height

from game.view.props.science_props import build_antenna_mast


def test_p04_r04_the_antenna_mast_is_a_well_formed_tall_prop_on_the_ground():
    prop = build_antenna_mast()
    check_prop(prop)
    assert bounds(prop.structure)[0][1] >= 0
    assert height(prop.structure) > 5
