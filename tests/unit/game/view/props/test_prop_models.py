# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/props/prop_models.py`."""

from typing import Any

import pytest
from helpers.geometry_checks import bounds, check_prop, footprint

from game.config.cars import CAR_IDS
from game.config.tile_buildings import BUILDING_MARGIN, TILE, TILE_MODELS
from game.view.props.prop_models import PROP_MODELS, make_car_models

PROP_IDS = sorted(PROP_MODELS)


def test_gfx_prop_02_every_prop_kind_has_one_model() -> None:
    assert PROP_IDS
    assert all(callable(factory) for factory in PROP_MODELS.values())


def test_gfx_prop_02_every_car_has_a_model() -> None:
    for car_id in CAR_IDS.values() if hasattr(CAR_IDS, "values") else CAR_IDS:
        assert car_id in PROP_MODELS


@pytest.mark.parametrize("prop_id", PROP_IDS)
def test_gfx_prop_04_every_prop_model_builds_a_well_formed_prop(prop_id: Any) -> None:
    prop = PROP_MODELS[prop_id]()
    assert check_prop(prop) > 0


@pytest.mark.parametrize("model", TILE_MODELS, ids=[m.id for m in TILE_MODELS])
def test_gfx_bldg_03_the_grid_models_keep_their_tile_footprint(model: Any) -> None:
    width, depth = footprint(PROP_MODELS[model.id]().structure)
    assert width == pytest.approx(model.tiles[0] * TILE.size - 2 * BUILDING_MARGIN)
    assert depth == pytest.approx(model.tiles[1] * TILE.size - 2 * BUILDING_MARGIN)


def test_d213_every_car_kind_has_its_own_body() -> None:
    """GFX-CAR-01: every kind's body differs in size or in triangle count."""
    models = make_car_models()
    bodies = set()
    for factory in models.values():
        structure = factory().structure
        low, high = bounds(structure)
        size = tuple(round(high[k] - low[k], 1) for k in range(3))
        bodies.add((size, len(structure.positions)))
    assert len(bodies) == len(models)
