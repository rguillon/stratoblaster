# Copyright (c) 2026 Renaud Guillon
"""Unit tests of every boss design.

The 20 mini and 20 final bosses of the game: their part counts (BOSS-13) and their stage patterns
(BOSS-21).
"""

from collections.abc import Callable
from itertools import combinations
from typing import Any

import pytest
from helpers.config_checks import original_parts

from core.systems.boss_pattern import BossVolley, _live
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
    assert len(MINI_IDS) == 20
    assert len(FINAL_IDS) == 20
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


def _key(value: object) -> str:
    """Return a text naming `value`: its fields that are set, by name, recursively.

    A launch's function is not part of it, so two volleys firing alike have the same text.
    """
    if isinstance(value, list | tuple):
        return "[" + ",".join(_key(item) for item in value) + "]"
    if callable(value):
        return "function"
    if hasattr(value, "__dict__"):
        fields = vars(value)
        names = [name for name in sorted(fields) if fields[name] is not None]
        return "{" + ",".join(name + ":" + _key(fields[name]) for name in names) + "}"
    return repr(value)


def _pattern_signature(volleys: list[BossVolley], intact: Callable[[str], bool]) -> str:
    """Return a text naming the volleys that still fire with only the `intact` pieces left.

    Two stages fire the same pattern when these texts are equal (BOSS-21).
    """
    return "|".join(sorted(_key(volley) for volley in volleys if _live(volley, intact)))


def _stage_signature(design: Any, stage: int, destroyed: frozenset[str]) -> str:
    """Return the pattern of `design`'s stage `stage`: the volleys of that stage that still fire.

    With `stage` parts destroyed (`destroyed`), as the world boss arms them (BOSS-20, BOSS-24).
    """
    stages = design.stages
    volleys = armed_pattern(design, stages[min(stage, len(stages) - 1)] or [])
    return _pattern_signature(volleys, lambda piece: piece == "core" or piece not in destroyed)


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=lambda d: d.id)
def test_boss_21_each_stage_fires_a_new_pattern_in_every_order_of_destruction(design: Any) -> None:
    """Any order of destruction is a chain of sets of destroyed parts.

    Each part destroyed moves the boss on, and the stage's pattern differs from the one before,
    whichever part goes next.
    """
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
def test_boss_21_the_last_stage_pattern_is_used_by_no_earlier_stage(design: Any) -> None:
    """The last stage (every part destroyed, its core's ring or spiral) fires a new pattern.

    The pattern is used in no earlier stage, whichever parts were destroyed by then.
    """
    parts = [part["id"] for part in original_parts(design)]
    last = len(parts)
    last_signature = _stage_signature(design, last, frozenset(parts))
    for stage in range(last):
        for destroyed in combinations(parts, stage):
            signature = _stage_signature(design, stage, frozenset(destroyed))
            assert signature != last_signature, (design.id, stage)
