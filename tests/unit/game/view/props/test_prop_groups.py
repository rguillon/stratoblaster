"""Unit tests of `src/game/view/props/prop_groups.py`."""

from game.config.tile_buildings import LOT_MODELS, TILE_GROUP_IDS, TILE_GROUPS
from game.view.props.prop_groups import (
    PROP_GROUPS,
    make_prop_groups,
    make_road_kit_group,
    make_tile_page,
    tile_notes,
    unique,
)
from game.view.props.prop_models import PROP_MODELS
from game.view.props.road_kit import ROAD_SAMPLE_ID


def test_p15_r10_unique_keeps_the_first_order_of_each_item():
    assert unique(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]
    assert unique([]) == []


def test_p15_r10_tile_notes_give_the_tiles_of_each_model():
    models = [TILE_GROUPS["homes"].models[0]]
    notes = tile_notes(models)
    assert notes == {models[0].id: f"{models[0].tiles[0]}×{models[0].tiles[1]} tiles"}


def test_p15_r10_the_road_kit_group_lists_the_kit_then_its_sample():
    group = make_road_kit_group()
    assert group.label == "Road kit"
    assert group.ids[-1] == ROAD_SAMPLE_ID
    assert group.notes[ROAD_SAMPLE_ID] == "every piece joined to straights"


def test_p15_r10_the_tile_page_is_the_road_kit_then_each_group_and_the_lots():
    page = make_tile_page()
    labels = [g.label for g in page]
    assert labels[0] == "Road kit"
    assert labels[1:-1] == ["Tiles: " + group_id for group_id in TILE_GROUP_IDS]
    assert labels[-1] == "Tiles: lots"
    assert [m.id for m in LOT_MODELS] == page[-1].ids


def test_p04_r04_the_prop_groups_name_only_known_models_once_each():
    groups = make_prop_groups()
    ids = [i for g in groups for i in g.ids]
    assert len(ids) == len(set(ids))
    assert set(ids) <= set(PROP_MODELS)
    assert all(len(g.ids) > 0 for g in groups)


def test_p04_r04_every_prop_model_is_on_the_page_once():
    ids = [i for g in make_prop_groups() for i in g.ids]
    assert set(ids) == set(PROP_MODELS)


def test_p04_r04_the_cars_come_last_and_the_groups_are_built_once():
    assert PROP_GROUPS[-1].label == "Cars"
    assert [g.label for g in PROP_GROUPS] == [g.label for g in make_prop_groups()]
