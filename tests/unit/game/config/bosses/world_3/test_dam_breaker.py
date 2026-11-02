# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_3/dam_breaker.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_3.dam_breaker import DAM_BREAKER


def test_fb_dam_breaker_08_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together (FB-DAM-BREAKER-07)."""
    assert_boss_design(DAM_BREAKER)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert DAM_BREAKER.id == DAM_BREAKER.id.lower()
    assert " " not in DAM_BREAKER.id
    assert "_" not in DAM_BREAKER.id


def test_fb_dam_breaker_07_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-DAM-BREAKER-06)."""
    stats = DAM_BREAKER.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_dam_breaker_10_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (FB-DAM-BREAKER-09)."""
    assert isinstance(DAM_BREAKER.rage, list)
    assert DAM_BREAKER.rage
    assert len(DAM_BREAKER.stages) == len(original_parts(DAM_BREAKER)) + 1
