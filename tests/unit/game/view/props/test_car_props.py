"""Unit tests of `src/game/view/props/car_props.py`."""

import pytest
from helpers.geometry_checks import bounds, check_prop

from game.config.prop_look import PROP_COLORS as C
from game.view.props.car_props import SHAPES, build_car
from game.view.props.prop_models import make_car_models

PAINT = C.containerRed


@pytest.mark.parametrize("shape", list(SHAPES))
def test_p04_r04_each_car_shape_is_a_well_formed_prop_with_its_lights(shape):
    prop = build_car(shape, PAINT)
    check_prop(prop)
    assert prop.lights is not None


@pytest.mark.parametrize("shape", list(SHAPES))
def test_p04_r04_a_car_stands_on_the_road_and_is_as_long_as_its_shape(shape):
    prop = build_car(shape, PAINT)
    low, high = bounds(prop.structure)
    assert low[1] >= 0
    assert high[2] - low[2] == pytest.approx(SHAPES[shape]["length"], rel=0.2)


def test_p04_r04_a_truck_is_longer_than_a_sedan():
    truck = bounds(build_car("truck", PAINT).structure)
    sedan = bounds(build_car("sedan", PAINT).structure)
    assert truck[1][2] - truck[0][2] > sedan[1][2] - sedan[0][2]


def test_d213_every_car_kind_has_its_own_body():
    models = make_car_models()
    bodies = set()
    for factory in models.values():
        structure = factory().structure
        low, high = bounds(structure)
        size = tuple(round(high[k] - low[k], 1) for k in range(3))
        bodies.add((size, len(structure.positions)))
    assert len(bodies) == len(models)
