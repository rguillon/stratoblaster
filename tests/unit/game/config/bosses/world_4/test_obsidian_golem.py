# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_4/obsidian_golem.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_4.obsidian_golem import OBSIDIAN_GOLEM


def test_fb_obsidian_golem_10_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together.

    Also FB-OBSIDIAN-GOLEM-11 and FB-OBSIDIAN-GOLEM-12.
    """
    assert_boss_design(OBSIDIAN_GOLEM)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert OBSIDIAN_GOLEM.id == OBSIDIAN_GOLEM.id.lower()
    assert " " not in OBSIDIAN_GOLEM.id
    assert "_" not in OBSIDIAN_GOLEM.id


def test_fb_obsidian_golem_09_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-OBSIDIAN-GOLEM-08)."""
    stats = OBSIDIAN_GOLEM.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_obsidian_golem_15_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (FB-OBSIDIAN-GOLEM-13)."""
    assert isinstance(OBSIDIAN_GOLEM.rage, list)
    assert OBSIDIAN_GOLEM.rage
    assert len(OBSIDIAN_GOLEM.stages) == len(original_parts(OBSIDIAN_GOLEM)) + 1
