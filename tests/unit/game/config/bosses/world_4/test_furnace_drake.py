# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_4/furnace_drake.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_4.furnace_drake import FURNACE_DRAKE


def test_mb_furnace_drake_09_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together (also MB-FURNACE-DRAKE-10)."""
    assert_boss_design(FURNACE_DRAKE)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert FURNACE_DRAKE.id == FURNACE_DRAKE.id.lower()
    assert " " not in FURNACE_DRAKE.id
    assert "_" not in FURNACE_DRAKE.id


def test_mb_furnace_drake_08_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (MB-FURNACE-DRAKE-07)."""
    stats = FURNACE_DRAKE.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_mb_furnace_drake_12_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (MB-FURNACE-DRAKE-11)."""
    assert isinstance(FURNACE_DRAKE.rage, list)
    assert FURNACE_DRAKE.rage
    assert len(FURNACE_DRAKE.stages) == len(original_parts(FURNACE_DRAKE)) + 1
