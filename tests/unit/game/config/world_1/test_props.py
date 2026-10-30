"""Unit tests of `src/game/config/world_1/props.py`."""

from game.config.world_1.props import WORLD_1_GROUPS, WORLD_1_PROPS
from game.config.world_1.scenery_coast import LEVEL_1_1, LEVEL_1_2
from game.config.world_1.scenery_country import LEVEL_1_3
from game.config.world_1.scenery_desert import LEVEL_1_4, LEVEL_1_5

SCENERY_LEVELS = [LEVEL_1_1, LEVEL_1_2, LEVEL_1_3, LEVEL_1_4, LEVEL_1_5]


def test_p06_r05_each_group_name_points_at_a_group_of_the_props_table() -> None:
    group_ids = {group.id for group in WORLD_1_PROPS.groups}
    for name, group_id in WORLD_1_GROUPS.items():
        assert group_id in group_ids, name


def test_p06_r05_each_group_is_a_non_empty_set_of_weighted_props() -> None:
    for group in WORLD_1_PROPS.groups:
        assert group.kinds, group.id
        for kind in group.kinds:
            assert kind.id and kind.weight > 0 and kind.footprint > 0, kind.id
            assert 0 < kind.scale[0] <= kind.scale[1], kind.id


def test_p06_r05_every_section_of_the_world_draws_from_a_known_group() -> None:
    group_ids = {group.id for group in WORLD_1_PROPS.groups}
    for level in SCENERY_LEVELS:
        for section in level.sections:
            for group_id in section["groups"] or []:
                assert group_id in group_ids, (level.id, group_id)


def test_p06_r05_the_props_table_has_lots_and_positive_spacing() -> None:
    assert WORLD_1_PROPS.lots
    assert WORLD_1_PROPS.cellSize > 0
