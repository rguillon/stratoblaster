# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_3/jaguar.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_3.jaguar import JAGUAR


def test_mb_jaguar_08_boss_design_is_well_formed() -> None:
    """Its parts (claw guns, tail cannon), guns and stage volleys fit together (MB-JAGUAR-07)."""
    assert_boss_design(JAGUAR)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert JAGUAR.id == JAGUAR.id.lower()
    assert " " not in JAGUAR.id
    assert "_" not in JAGUAR.id


def test_mb_jaguar_07_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (MB-JAGUAR-06)."""
    stats = JAGUAR.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_mb_jaguar_10_boss_has_its_stage_count() -> None:
    """One stage pattern more than its parts (MB-JAGUAR-09)."""
    assert len(JAGUAR.stages) == len(original_parts(JAGUAR)) + 1
