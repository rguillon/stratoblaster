# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_2/narwhal.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_2.narwhal import NARWHAL


def test_fb_narwhal_08_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together.

    Parts: horn lance, torpedo tubes (FB-NARWHAL-09), ballast pods (FB-NARWHAL-10). Guns and stage
    volleys: FB-NARWHAL-11.
    """
    assert_boss_design(NARWHAL)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert NARWHAL.id == NARWHAL.id.lower()
    assert " " not in NARWHAL.id
    assert "_" not in NARWHAL.id


def test_fb_narwhal_15_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-NARWHAL-07)."""
    stats = NARWHAL.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_narwhal_12_boss_has_its_stage_count() -> None:
    """One stage pattern more than its parts (FB-NARWHAL-11)."""
    assert len(NARWHAL.stages) == len(original_parts(NARWHAL)) + 1
