"""Unit tests of `src/game/config/world_2/waves.py`."""

import pytest
from helpers.config_checks import assert_beats_well_formed, enemy_kind_ids

from game.config.world_2.waves import (
    PLAN_2_1,
    PLAN_2_2,
    PLAN_2_3,
    PLAN_2_4,
    PLAN_2_5,
    WORLD_2_FILLERS,
    compose_beats,
)

KINDS = enemy_kind_ids()
PLANS = [PLAN_2_1, PLAN_2_2, PLAN_2_3, PLAN_2_4, PLAN_2_5]


@pytest.mark.parametrize("plan", PLANS)
def test_p08_r08_a_plan_composes_beats_that_name_kinds_and_sides_in_order(plan) -> None:
    beats = compose_beats(plan)
    assert beats
    assert_beats_well_formed(beats, KINDS)
    assert beats[0][0] >= plan["from"]
    assert beats[-1][0] <= plan["to"]


def test_p08_r08_each_filler_names_known_kinds_and_its_gap_shrinks() -> None:
    for level_id, filler in WORLD_2_FILLERS.items():
        assert filler["kinds"], level_id
        assert set(filler["kinds"]) <= KINDS, level_id
        start, end = filler["maxGap"]
        assert start >= end > 0, level_id
