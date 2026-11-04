# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_3/sky_temple.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_3.sky_temple import SKY_TEMPLE


def test_fb_sky_temple_09_boss_design_is_well_formed() -> None:
    """Its parts (obelisks, beacon), guns and stage volleys fit together (FB-SKY-TEMPLE-08)."""
    assert_boss_design(SKY_TEMPLE)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert SKY_TEMPLE.id == SKY_TEMPLE.id.lower()
    assert " " not in SKY_TEMPLE.id
    assert "_" not in SKY_TEMPLE.id


def test_fb_sky_temple_08_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-SKY-TEMPLE-07)."""
    stats = SKY_TEMPLE.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_sky_temple_11_boss_has_its_stage_count() -> None:
    """One stage pattern more than its parts (FB-SKY-TEMPLE-10)."""
    assert len(SKY_TEMPLE.stages) == len(original_parts(SKY_TEMPLE)) + 1
