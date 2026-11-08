# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/wave_plans.py` (ENM-50, WLD-N-17, WLD-N-19)."""

import itertools

import pytest
from helpers.config_checks import assert_beats_well_formed, enemy_kind_ids

from game.config.enemy_tiers import tier_kinds
from game.config.wave_plans import (
    KIND_ENTRY,
    SETTLE,
    compose_beats,
    enemies_of,
    kinds_of,
    level_filler,
    level_plan,
    tier_mix,
    wave_duration,
    world_fillers,
)

LEVELS = [(world, level) for world in range(1, 5) for level in range(1, 6)]


def test_enm_50_every_kind_has_an_entry() -> None:
    kinds = {kind for world in range(1, 5) for kind in tier_kinds(world)}
    assert set(KIND_ENTRY.keys()) == kinds


def _tiers_of(world: int, level: int) -> list[int]:
    return [pair[0] for pair in tier_mix(world, level)]


@pytest.mark.parametrize(("world", "level"), LEVELS)
def test_enm_50_a_level_names_only_kinds_of_its_tiers_and_every_one_of_them(
    world: int, level: int
) -> None:
    allowed = {kind for tier in _tiers_of(world, level) for kind in tier_kinds(tier)}
    beats = compose_beats(level_plan(world, level))
    assert beats
    assert {beat[1] for beat in beats} == allowed
    assert set(level_filler(world, level).kinds) <= allowed
    assert set(kinds_of(world, level)) == allowed
    assert_beats_well_formed(beats, enemy_kind_ids())


def test_enm_50_the_tier_mix_of_each_level() -> None:
    """Each level's share of the ships by tier (D-283).

    World 1 from 80 / 20 % to 60 / 40 %, Worlds 2 and 3 60 % their tier with the rest sliding from
    the tier below to the one above, World 4 up to tier 4 only.
    """
    assert [tier_mix(1, level) for level in range(1, 6)] == [
        [[1, 80], [2, 20]],
        [[1, 75], [2, 25]],
        [[1, 70], [2, 30]],
        [[1, 65], [2, 35]],
        [[1, 60], [2, 40]],
    ]
    assert tier_mix(2, 1) == [[2, 60], [1, 40]]
    assert tier_mix(2, 3) == [[2, 60], [1, 20], [3, 20]]
    assert tier_mix(2, 5) == [[2, 60], [3, 40]]
    assert tier_mix(3, 2) == [[3, 60], [2, 30], [4, 10]]
    assert tier_mix(4, 1) == [[4, 60], [3, 40]]
    assert tier_mix(4, 5) == [[4, 100]]
    for world, level in LEVELS:
        assert sum(pair[1] for pair in tier_mix(world, level)) == 100


def test_enm_50_a_wasp_group_counts_as_its_swarm() -> None:
    assert enemies_of(2, "hornet") == 3
    assert enemies_of(2, "wasp") == 15


def test_wld_1_25_the_first_level_filler_is_the_hornet_only_which_never_shoots() -> None:
    assert level_filler(1, 1).kinds == ["hornet"]
    assert level_filler(1, 2).kinds == ["hornet", "scout", "wasp", "strafer"]


def test_wld_2_19_the_filler_gap_shrinks_and_every_level_has_one() -> None:
    for world in range(1, 5):
        fillers = world_fillers(world)
        assert sorted(fillers.keys()) == [f"{world}-{level}" for level in range(1, 6)]
        for filler in fillers.values():
            start, end = filler["maxGap"]
            assert start >= end > 0


def test_a_kind_met_again_comes_in_another_way_then_mirrored() -> None:
    plan = {**level_plan(1, 4), "to": 700}
    beats = [beat for beat in compose_beats(plan) if beat[1] == "hornet"]
    ways = len(KIND_ENTRY["hornet"])
    assert len(beats) > ways
    # Four ways in turn: a line across the top, a column down a side, two pincers.
    assert [beat[4] for beat in beats[:ways]] == ["top", "left", "top", "left"]
    assert len({(beat[4], beat[5]) for beat in beats[:ways]}) == ways
    # The second time round the list is mirrored: the side column comes from the right.
    assert beats[ways][4] == "top"
    assert beats[ways][5] == pytest.approx(1 - beats[0][5])
    assert beats[ways + 1][4] == "right"


def test_a_diver_comes_in_from_the_sides_too() -> None:
    for world in range(1, 5):
        diver = tier_kinds(world)[0]
        if diver not in ("hornet", "wasp"):
            continue
        long_plan = {**level_plan(world, 5), "to": 900}
        sides = {beat[4] for beat in compose_beats(long_plan) if beat[1] == diver}
        assert {"top", "left", "right"} <= sides, diver


def test_a_pincer_beat_carries_its_alternate_flag() -> None:
    pincers = [beat for beat in compose_beats(level_plan(1, 1)) if len(beat) == 8]
    assert pincers
    assert all(beat[7] == 1 for beat in pincers)


@pytest.mark.parametrize(("world", "level"), LEVELS)
def test_a_wave_is_over_before_the_next_kind_comes_in(world: int, level: int) -> None:
    beats = compose_beats(level_plan(world, level))
    for current, following in itertools.pairwise(beats):
        over = current[0] + wave_duration(current[2], current[3]) + SETTLE
        assert following[0] >= over - 0.1, (current, following)


def test_a_side_kind_comes_from_the_other_side_when_mirrored() -> None:
    long_plan = {**level_plan(2, 5), "to": 900}
    beats = [beat for beat in compose_beats(long_plan) if beat[1] == "strafer"]
    ways = len(KIND_ENTRY.strafer)
    first = [beat[4] for beat in beats[:ways]]
    mirrored = [beat[4] for beat in beats[ways : 2 * ways]]
    assert "left" in first
    assert "top" in first
    # The second time round, a way from the left comes from the right; one from the top (a
    # vertical pass) stays from the top, its position mirrored.
    assert mirrored == [{"left": "right"}.get(side, side) for side in first]
    for plain, flipped in zip(beats[:ways], beats[ways : 2 * ways], strict=True):
        assert flipped[5] == pytest.approx(1 - plain[5])


def test_wld_2_22_a_plan_fills_up_and_its_groups_grow() -> None:
    plan = level_plan(2, 3)
    beats = compose_beats(plan)
    # The breather between a wave's end and the next beat shrinks over the level.
    breathers = [
        b[0] - a[0] - wave_duration(a[2], a[3]) - SETTLE for a, b in itertools.pairwise(beats)
    ]
    assert breathers[0] > breathers[-1]
    assert beats[0][0] >= plan["from"]
    assert beats[-1][0] <= plan["to"]
    firsts = [beat[2] for beat in beats if beat[1] == "wasp"]
    assert firsts[-1] >= firsts[0]


def test_each_world_is_harder_than_the_one_before() -> None:
    assert level_plan(1, 1)["gap"][0] > level_plan(2, 1)["gap"][0] > level_plan(4, 1)["gap"][0]
    assert level_plan(3, 1)["growth"] < level_plan(3, 5)["growth"]
    assert level_plan(1, 1)["to"] < level_plan(2, 1)["to"]
