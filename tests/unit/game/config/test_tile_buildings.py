"""Unit tests of `src/game/config/tile_buildings.py`."""

import math

import pytest

from game.config.tile_buildings import (
    BUILDING_MARGIN,
    LOT_KINDS,
    LOT_MODELS,
    TILE,
    TILE_GROUP_IDS,
    TILE_GROUPS,
    TILE_MODELS,
    all_models,
    tile_kind,
    tile_kinds,
    unique_by_id,
)


def test_p15_r01_every_tile_model_has_a_unique_id_and_a_positive_footprint() -> None:
    ids = [m.id for m in TILE_MODELS]
    assert len(ids) == len(set(ids))
    for m in TILE_MODELS:
        assert m.id.startswith("tile-"), m.id
        assert m.tiles[0] >= 1 and m.tiles[1] >= 1, m.id


def test_p15_r01_every_tile_group_lists_its_models_and_range() -> None:
    assert list(TILE_GROUPS.keys()) == TILE_GROUP_IDS
    for group_id in TILE_GROUP_IDS:
        group = TILE_GROUPS[group_id]
        assert group.models, group_id
        assert group.range is not None, group_id


def test_p15_r01_lot_models_are_the_small_lots_of_the_city_with_unique_ids() -> None:
    ids = [m.id for m in LOT_MODELS]
    assert len(ids) == len(set(ids))
    assert all(m.tiles[0] >= 1 and m.tiles[1] >= 1 for m in LOT_MODELS)


def test_p15_r01_lot_kinds_have_their_weight_scale_and_tiles() -> None:
    assert LOT_KINDS
    for lot in LOT_KINDS:
        assert lot.weight > 0
        assert lot.scale[0] > 0 and lot.scale[1] > 0


def test_p15_r01_tile_and_building_margin_constants() -> None:
    assert TILE.size == 10
    assert TILE.sidewalk == 2
    assert pytest.approx(0.5) == BUILDING_MARGIN


def test_p15_r01_tile_kind_takes_its_footprint_from_the_tiles_diagonal() -> None:
    m = TILE_MODELS[0]
    kind = tile_kind(m, 0.5)
    assert kind.id == m.id
    assert kind.weight == 0.5
    w, d = m.tiles
    assert kind.footprint == pytest.approx(math.hypot(w, d) * TILE.size / 2)


def test_p15_r01_tile_kinds_of_a_group_share_its_weight_evenly() -> None:
    kinds = tile_kinds("homes", 2)
    assert len(kinds) == len(TILE_GROUPS["homes"].models)
    assert sum(k.weight for k in kinds) == pytest.approx(2)


def test_p15_r01_all_models_has_every_group_model_and_every_lot_model() -> None:
    models = all_models()
    expected = sum(len(TILE_GROUPS[g].models) for g in TILE_GROUP_IDS) + len(LOT_MODELS)
    assert len(models) == expected


def test_p15_r01_unique_by_id_keeps_the_first_of_each_id_in_order() -> None:
    a = tile_kind(TILE_MODELS[0], 1)
    b = tile_kind(TILE_MODELS[1], 1)
    out = unique_by_id([a, b, a])
    assert [m.id for m in out] == [TILE_MODELS[0].id, TILE_MODELS[1].id]
