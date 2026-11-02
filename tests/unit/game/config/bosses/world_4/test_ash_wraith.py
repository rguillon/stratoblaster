# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_4/ash_wraith.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_4.ash_wraith import ASH_WRAITH


def test_mb_ash_wraith_08_boss_design_is_well_formed() -> None:
    """Its parts (pods, eye), guns and stage volleys fit together (MB-ASH-WRAITH-09)."""
    assert_boss_design(ASH_WRAITH)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert ASH_WRAITH.id == ASH_WRAITH.id.lower()
    assert " " not in ASH_WRAITH.id
    assert "_" not in ASH_WRAITH.id


def test_mb_ash_wraith_07_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (MB-ASH-WRAITH-06)."""
    stats = ASH_WRAITH.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_mb_ash_wraith_11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (MB-ASH-WRAITH-10)."""
    assert isinstance(ASH_WRAITH.rage, list)
    assert ASH_WRAITH.rage
    assert len(ASH_WRAITH.stages) == len(original_parts(ASH_WRAITH)) + 1
