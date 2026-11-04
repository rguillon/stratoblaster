# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_4/geyser_rig.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_4.geyser_rig import GEYSER_RIG


def test_fb_geyser_rig_10_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together (also FB-GEYSER-RIG-11)."""
    assert_boss_design(GEYSER_RIG)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert GEYSER_RIG.id == GEYSER_RIG.id.lower()
    assert " " not in GEYSER_RIG.id
    assert "_" not in GEYSER_RIG.id


def test_fb_geyser_rig_09_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-GEYSER-RIG-08)."""
    stats = GEYSER_RIG.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_geyser_rig_14_boss_has_its_stage_count() -> None:
    """One stage pattern more than its parts (FB-GEYSER-RIG-13)."""
    assert len(GEYSER_RIG.stages) == len(original_parts(GEYSER_RIG)) + 1
