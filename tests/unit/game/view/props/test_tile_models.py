"""Unit tests of `src/game/view/props/tile_models.py`."""

import pytest
from helpers.geometry_checks import check_prop, footprint

from game.config.tile_buildings import BUILDING_MARGIN, TILE, TILE_MODELS
from game.view.props.tile_models import BUILDERS, TILE_PROP_MODELS, build_tile_model

MODEL_IDS = [m.id for m in TILE_MODELS]


def test_p15_r07_every_model_of_the_grid_has_a_factory():
    assert sorted(TILE_PROP_MODELS) == sorted(MODEL_IDS)


def test_p15_r09_every_archetype_of_the_grid_has_a_builder():
    archetypes = {m.archetype for m in TILE_MODELS}
    assert archetypes <= set(BUILDERS)


@pytest.mark.parametrize("model", TILE_MODELS, ids=MODEL_IDS)
def test_p15_r07_each_model_fills_its_tiles_less_the_margin(model):
    prop = TILE_PROP_MODELS[model.id]()
    check_prop(prop)
    width, depth = footprint(prop.structure)
    assert width == pytest.approx(model.tiles[0] * TILE.size - 2 * BUILDING_MARGIN)
    assert depth == pytest.approx(model.tiles[1] * TILE.size - 2 * BUILDING_MARGIN)


def test_p15_r07_a_model_is_built_the_same_way_each_time():
    model = TILE_MODELS[0]
    a = build_tile_model(model)
    b = build_tile_model(model)
    assert a.structure.positions == b.structure.positions
    assert a.structure.colors == b.structure.colors
