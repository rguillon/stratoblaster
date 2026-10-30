"""Unit tests of `src/game/view/props/wind_turbine.py`."""

from helpers.geometry_checks import bounds, check_prop, height

from game.view.props.wind_turbine import build_wind_turbine


def test_p04_r04_the_wind_turbine_is_a_well_formed_tall_prop_on_the_ground():
    prop = build_wind_turbine()
    check_prop(prop)
    assert bounds(prop.structure)[0][1] >= 0
    assert height(prop.structure) > 5
