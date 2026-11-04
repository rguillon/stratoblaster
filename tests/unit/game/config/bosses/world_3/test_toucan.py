# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_3/toucan.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_3.toucan import TOUCAN


def test_mb_toucan_09_boss_design_is_well_formed() -> None:
    """Its parts (wing pods, beak), guns and stage volleys fit together (MB-TOUCAN-08)."""
    assert_boss_design(TOUCAN)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert TOUCAN.id == TOUCAN.id.lower()
    assert " " not in TOUCAN.id
    assert "_" not in TOUCAN.id


def test_mb_toucan_08_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (MB-TOUCAN-07)."""
    stats = TOUCAN.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_mb_toucan_11_boss_has_its_stage_count() -> None:
    """One stage pattern more than its parts (MB-TOUCAN-10)."""
    assert len(TOUCAN.stages) == len(original_parts(TOUCAN)) + 1
