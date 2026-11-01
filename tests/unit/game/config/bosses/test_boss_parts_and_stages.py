"""Unit tests of every boss design (the 20 mini and 20 final bosses of the game): their part counts
(BOSS-13) and their stage patterns (BOSS-21)."""

from itertools import combinations

import pytest
from helpers.config_checks import original_parts

from core.systems.boss_pattern import pattern_signature
from game.config.world_1.bosses import WORLD_1_BOSSES
from game.config.world_2.bosses import WORLD_2_BOSSES
from game.config.world_3.bosses import WORLD_3_BOSSES
from game.config.world_4.bosses import WORLD_4_BOSSES
from game.sim.boss_build import armed_pattern
from game.sim.boss_kinds import BOSS_DESIGNS

WORLD_TABLES = [WORLD_1_BOSSES, WORLD_2_BOSSES, WORLD_3_BOSSES, WORLD_4_BOSSES]
MINI_IDS = {entry["mini"] for table in WORLD_TABLES for entry in table.values()}
FINAL_IDS = {entry["final"] for table in WORLD_TABLES for entry in table.values()}


def test_boss_13_the_game_has_20_mini_bosses_and_20_final_bosses() -> None:
    designs = {design.id for design in BOSS_DESIGNS}
    assert len(designs) == len(BOSS_DESIGNS) == 40
    assert len(MINI_IDS) == 20 and len(FINAL_IDS) == 20
    assert designs == MINI_IDS | FINAL_IDS
    assert MINI_IDS.isdisjoint(FINAL_IDS)


def test_boss_13_every_mini_boss_comes_in_with_2_or_3_parts() -> None:
    """The parts there from the start (its hidden weapons, revealed later, come on top)."""
    for design in BOSS_DESIGNS:
        if design.id in MINI_IDS:
            count = len(original_parts(design))
            assert 2 <= count <= 3, (design.id, count)


def test_boss_13_every_final_boss_comes_in_with_4_to_6_parts() -> None:
    for design in BOSS_DESIGNS:
        if design.id in FINAL_IDS:
            count = len(original_parts(design))
            assert 4 <= count <= 6, (design.id, count)


def _stage_signature(design, stage: int, destroyed: frozenset[str]) -> str:
    """The pattern of `design`'s stage `stage` (`stage` parts destroyed, `destroyed`): the volleys
    of that stage that still fire, as the world boss arms them (BOSS-20, BOSS-24)."""
    stages = design.stages
    volleys = armed_pattern(design, stages[min(stage, len(stages) - 1)] or [])
    return pattern_signature(volleys, lambda piece: piece == "core" or piece not in destroyed)


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=lambda d: d.id)
def test_boss_21_each_stage_fires_a_new_pattern_in_every_order_of_destruction(design) -> None:
    """Any order of destruction is a chain of sets of destroyed parts: each part destroyed moves
    the boss on, and the stage's pattern differs from the one before, whichever part goes next."""
    parts = [part["id"] for part in original_parts(design)]
    for size in range(len(parts)):
        for before in combinations(parts, size):
            destroyed = frozenset(before)
            previous = _stage_signature(design, size, destroyed)
            for part in parts:
                if part in destroyed:
                    continue
                after = _stage_signature(design, size + 1, destroyed | {part})
                assert after != previous, (design.id, sorted(destroyed), part)


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=lambda d: d.id)
def test_boss_21_the_last_stage_pattern_is_used_by_no_earlier_stage(design) -> None:
    """The last stage (every part destroyed, its core's ring or spiral) fires a pattern used in no
    earlier stage, whichever parts were destroyed by then."""
    parts = [part["id"] for part in original_parts(design)]
    last = len(parts)
    last_signature = _stage_signature(design, last, frozenset(parts))
    for stage in range(last):
        for destroyed in combinations(parts, stage):
            signature = _stage_signature(design, stage, frozenset(destroyed))
            assert signature != last_signature, (design.id, stage)
