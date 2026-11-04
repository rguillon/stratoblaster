# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_3/river_leviathan.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_3.river_leviathan import RIVER_LEVIATHAN


def test_fb_river_leviathan_10_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together (FB-RIVER-LEVIATHAN-09)."""
    assert_boss_design(RIVER_LEVIATHAN)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert RIVER_LEVIATHAN.id == RIVER_LEVIATHAN.id.lower()
    assert " " not in RIVER_LEVIATHAN.id
    assert "_" not in RIVER_LEVIATHAN.id


def test_fb_river_leviathan_09_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-RIVER-LEVIATHAN-08)."""
    stats = RIVER_LEVIATHAN.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_river_leviathan_12_boss_has_its_stage_count() -> None:
    """One stage pattern more than its parts (FB-RIVER-LEVIATHAN-11)."""
    assert len(RIVER_LEVIATHAN.stages) == len(original_parts(RIVER_LEVIATHAN)) + 1
