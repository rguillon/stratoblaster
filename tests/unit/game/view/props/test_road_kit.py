"""Unit tests of `src/game/view/props/road_kit.py`."""

import pytest
from helpers.geometry_checks import check_colored, check_prop

from game.config.tile_buildings import TILE
from game.view.props.road_kit import (
    ROAD_KIT,
    ROAD_KIT_MODELS,
    ROAD_KIT_NOTES,
    ROAD_KIT_PIECES,
    ROAD_SAMPLE_ID,
    SIZES,
    build_sample,
)


def test_p15_r03_the_kit_has_straights_turns_tees_and_crosses_for_each_size():
    ids = [kit.id for kit in ROAD_KIT]
    assert len(ids) == len(set(ids))
    assert SIZES == [1, 2, 3]
    assert ROAD_KIT_PIECES
    assert len(ROAD_KIT) >= len(SIZES) * 4


def test_p15_r03_every_kit_piece_is_a_model_and_has_a_note():
    ids = [kit.id for kit in ROAD_KIT]
    assert set(ids) <= set(ROAD_KIT_MODELS)
    assert set(ids) <= set(ROAD_KIT_NOTES)


@pytest.mark.parametrize("kit_id", [kit.id for kit in ROAD_KIT])
def test_p15_r03_every_kit_piece_builds_a_well_formed_prop(kit_id):
    prop = ROAD_KIT_MODELS[kit_id]()
    check_prop(prop)


def test_p15_r10_the_sample_is_a_layout_of_joined_pieces():
    sample = build_sample()
    check_prop(sample)
    assert ROAD_SAMPLE_ID in ROAD_KIT_MODELS
    width, depth = (
        max(sample.structure.positions[0::3]) - min(sample.structure.positions[0::3]),
        max(sample.structure.positions[2::3]) - min(sample.structure.positions[2::3]),
    )
    assert width > TILE.size
    assert depth > TILE.size
    check_colored(sample.structure)
