"""Unit tests of `src/game/config/world_4/waves.py`."""

import pytest
from helpers.config_checks import assert_beats_well_formed, enemy_kind_ids

from game.config.world_2.waves import compose_beats
from game.config.world_4.waves import (
    PLAN_4_1,
    PLAN_4_2,
    PLAN_4_3,
    PLAN_4_4,
    PLAN_4_5,
    WORLD_4_FILLERS,
)

KINDS = enemy_kind_ids()
PLANS = [PLAN_4_1, PLAN_4_2, PLAN_4_3, PLAN_4_4, PLAN_4_5]


@pytest.mark.parametrize("plan", PLANS)
def test_p10_r09_a_plan_composes_beats_that_name_kinds_and_sides_in_order(plan) -> None:
    beats = compose_beats(plan)
    assert beats
    assert_beats_well_formed(beats, KINDS)
    assert beats[0][0] >= plan["from"]
    assert beats[-1][0] <= plan["to"]


def test_p10_r09_each_filler_names_known_kinds_and_its_gap_shrinks() -> None:
    for level_id, filler in WORLD_4_FILLERS.items():
        assert filler["kinds"], level_id
        assert set(filler["kinds"]) <= KINDS, level_id
        start, end = filler["maxGap"]
        assert start >= end > 0, level_id
