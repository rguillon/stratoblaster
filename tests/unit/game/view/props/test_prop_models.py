"""Unit tests of `src/game/view/props/prop_models.py`."""

import pytest
from helpers.geometry_checks import check_prop, footprint

from game.config.cars import CAR_IDS
from game.config.tile_buildings import BUILDING_MARGIN, TILE, TILE_MODELS
from game.view.props.prop_models import PROP_MODELS

PROP_IDS = sorted(PROP_MODELS)


def test_p04_r04_every_prop_kind_has_one_model():
    assert PROP_IDS
    assert all(callable(factory) for factory in PROP_MODELS.values())


def test_p04_r04_every_car_has_a_model():
    for car_id in CAR_IDS.values() if hasattr(CAR_IDS, "values") else CAR_IDS:
        assert car_id in PROP_MODELS


@pytest.mark.parametrize("prop_id", PROP_IDS)
def test_p04_r04_every_prop_model_builds_a_well_formed_prop(prop_id):
    prop = PROP_MODELS[prop_id]()
    assert check_prop(prop) > 0


@pytest.mark.parametrize("model", TILE_MODELS, ids=[m.id for m in TILE_MODELS])
def test_p15_r07_the_grid_models_keep_their_tile_footprint(model):
    width, depth = footprint(PROP_MODELS[model.id]().structure)
    assert width == pytest.approx(model.tiles[0] * TILE.size - 2 * BUILDING_MARGIN)
    assert depth == pytest.approx(model.tiles[1] * TILE.size - 2 * BUILDING_MARGIN)
