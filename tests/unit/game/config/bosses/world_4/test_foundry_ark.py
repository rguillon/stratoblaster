# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_4/foundry_ark.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_4.foundry_ark import FOUNDRY_ARK


def test_fb_foundry_ark_10_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together (also FB-FOUNDRY-ARK-11)."""
    assert_boss_design(FOUNDRY_ARK)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert FOUNDRY_ARK.id == FOUNDRY_ARK.id.lower()
    assert " " not in FOUNDRY_ARK.id
    assert "_" not in FOUNDRY_ARK.id


def test_fb_foundry_ark_09_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-FOUNDRY-ARK-08)."""
    stats = FOUNDRY_ARK.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_foundry_ark_15_boss_has_its_stage_count() -> None:
    """One stage pattern more than its parts (FB-FOUNDRY-ARK-13)."""
    assert len(FOUNDRY_ARK.stages) == len(original_parts(FOUNDRY_ARK)) + 1
