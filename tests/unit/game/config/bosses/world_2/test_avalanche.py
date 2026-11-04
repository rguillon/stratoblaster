# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_2/avalanche.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_2.avalanche import AVALANCHE


def test_mb_avalanche_09_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together.

    Parts: drills, rock hopper (MB-AVALANCHE-10). Guns and stage volleys: MB-AVALANCHE-11.
    """
    assert_boss_design(AVALANCHE)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert AVALANCHE.id == AVALANCHE.id.lower()
    assert " " not in AVALANCHE.id
    assert "_" not in AVALANCHE.id


def test_mb_avalanche_14_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (MB-AVALANCHE-08)."""
    stats = AVALANCHE.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_mb_avalanche_12_boss_has_its_stage_count() -> None:
    """One stage pattern more than its parts (MB-AVALANCHE-11)."""
    assert len(AVALANCHE.stages) == len(original_parts(AVALANCHE)) + 1
