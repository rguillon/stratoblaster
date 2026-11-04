# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/wave_plans.py` (ENM-50, WLD-N-17, WLD-N-19)."""

import itertools

import pytest
from helpers.config_checks import assert_beats_well_formed, enemy_kind_ids

from game.config.enemy_tiers import tier_kinds
from game.config.wave_plans import (
    KIND_ENTRY,
    PHRASE_LENGTH,
    compose_beats,
    kinds_of,
    level_filler,
    level_phrases,
    level_plan,
    roles_of,
    world_fillers,
)

LEVELS = [(world, level) for world in range(1, 5) for level in range(1, 6)]


def test_enm_50_every_kind_has_an_entry() -> None:
    kinds = {kind for world in range(1, 5) for kind in tier_kinds(world)}
    assert set(KIND_ENTRY.keys()) == kinds


@pytest.mark.parametrize(("world", "level"), LEVELS)
def test_enm_50_a_level_names_only_kinds_of_its_worlds_tier(world: int, level: int) -> None:
    allowed = set(tier_kinds(world))
    beats = compose_beats(level_plan(world, level))
    assert beats
    assert {beat[1] for beat in beats} <= allowed
    assert set(level_filler(world, level).kinds) <= allowed
    assert set(kinds_of(world, level)) <= allowed
    assert_beats_well_formed(beats, enemy_kind_ids())


def test_enm_50_world_1_brings_one_more_kind_each_level_and_the_others_start_with_three() -> None:
    assert [len(roles_of(1, level)) for level in range(1, 6)] == [2, 3, 4, 5, 5]
    for world in (2, 3, 4):
        assert [len(roles_of(world, level)) for level in range(1, 6)] == [3, 4, 5, 5, 5]
    assert kinds_of(1, 1) == ["hornet", "scout"]
    assert set(kinds_of(1, 5)) == set(tier_kinds(1))


def test_enm_50_the_first_level_filler_is_the_diver_only_which_never_shoots() -> None:
    assert level_filler(1, 1).kinds == ["hornet"]
    assert level_filler(1, 2).kinds == ["hornet", "scout", "hornet", "scout"]


def test_wld_2_19_the_filler_gap_shrinks_and_every_level_has_one() -> None:
    for world in range(1, 5):
        fillers = world_fillers(world)
        assert sorted(fillers.keys()) == [f"{world}-{level}" for level in range(1, 6)]
        for filler in fillers.values():
            start, end = filler["maxGap"]
            assert start >= end > 0


def test_a_kind_met_twice_in_a_cycle_comes_mirrored_the_second_time() -> None:
    phrases = level_phrases(1, 4)
    divers = [phrase for phrase in phrases if phrase[0] == "hornet"]
    assert len(divers) == 3
    assert divers[0][4] == pytest.approx(0.15)
    assert divers[1][4] == pytest.approx(0.85)
    assert divers[0][5] == pytest.approx(0.23)
    assert divers[1][5] == pytest.approx(-0.23)


def test_a_side_kind_comes_from_the_other_side_when_mirrored() -> None:
    phrases = level_phrases(2, 5)
    strafers = [phrase for phrase in phrases if phrase[0] == "strafer"]
    assert [phrase[3] for phrase in strafers[:2]] == ["left", "right"]
    assert len(strafers[0]) == PHRASE_LENGTH


def test_wld_2_22_a_plan_fills_up_and_its_groups_grow() -> None:
    plan = level_plan(2, 3)
    beats = compose_beats(plan)
    gaps = [b[0] - a[0] for a, b in itertools.pairwise(beats)]
    assert gaps[0] > gaps[-1]
    assert beats[0][0] >= plan["from"]
    assert beats[-1][0] <= plan["to"]
    firsts = [beat[2] for beat in beats if beat[1] == "wasp"]
    assert firsts[-1] >= firsts[0]


def test_each_world_is_harder_than_the_one_before() -> None:
    assert level_plan(1, 1)["gap"][0] > level_plan(2, 1)["gap"][0] > level_plan(4, 1)["gap"][0]
    assert level_plan(3, 1)["growth"] < level_plan(3, 5)["growth"]
    assert level_plan(1, 1)["to"] < level_plan(2, 1)["to"]
