"""Unit tests of `src/game/config/world_3/waves.py`."""

import pytest
from helpers.config_checks import assert_beats_well_formed, enemy_kind_ids

from game.config.world_2.waves import compose_beats
from game.config.world_3.waves import (
    PLAN_3_1,
    PLAN_3_2,
    PLAN_3_3,
    PLAN_3_4,
    PLAN_3_5,
    WORLD_3_FILLERS,
)

KINDS = enemy_kind_ids()
PLANS = [PLAN_3_1, PLAN_3_2, PLAN_3_3, PLAN_3_4, PLAN_3_5]


@pytest.mark.parametrize("plan", PLANS)
def test_p09_r07_a_plan_composes_beats_that_name_kinds_and_sides_in_order(plan) -> None:
    beats = compose_beats(plan)
    assert beats
    assert_beats_well_formed(beats, KINDS)
    assert beats[0][0] >= plan["from"]
    assert beats[-1][0] <= plan["to"]


def test_p09_r07_each_filler_names_known_kinds_and_its_gap_shrinks() -> None:
    for level_id, filler in WORLD_3_FILLERS.items():
        assert filler["kinds"], level_id
        assert set(filler["kinds"]) <= KINDS, level_id
        start, end = filler["maxGap"]
        assert start >= end > 0, level_id
