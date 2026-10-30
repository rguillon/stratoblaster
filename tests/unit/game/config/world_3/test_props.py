"""Unit tests of `src/game/config/world_3/props.py`."""

from game.config.world_3.props import WORLD_3_GROUPS, WORLD_3_PROPS
from game.config.world_3.scenery import LEVEL_3_1, LEVEL_3_2, LEVEL_3_3, LEVEL_3_4, LEVEL_3_5

SCENERY_LEVELS = [LEVEL_3_1, LEVEL_3_2, LEVEL_3_3, LEVEL_3_4, LEVEL_3_5]


def test_p09_r03_each_group_name_points_at_a_group_of_the_props_table() -> None:
    group_ids = {group.id for group in WORLD_3_PROPS.groups}
    for name, group_id in WORLD_3_GROUPS.items():
        assert group_id in group_ids, name


def test_p09_r03_each_group_is_a_non_empty_set_of_weighted_props() -> None:
    for group in WORLD_3_PROPS.groups:
        assert group.kinds, group.id
        for kind in group.kinds:
            assert kind.id and kind.weight > 0 and kind.footprint > 0, kind.id
            assert 0 < kind.scale[0] <= kind.scale[1], kind.id


def test_p09_r03_every_section_of_the_world_draws_from_a_known_group() -> None:
    group_ids = {group.id for group in WORLD_3_PROPS.groups}
    for level in SCENERY_LEVELS:
        for section in level.sections:
            for group_id in section["groups"] or []:
                assert group_id in group_ids, (level.id, group_id)


def test_p09_r03_the_props_table_has_lots_and_positive_spacing() -> None:
    assert WORLD_3_PROPS.lots
    assert WORLD_3_PROPS.cellSize > 0
