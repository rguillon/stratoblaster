# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_3/mosquito.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_3.mosquito import MOSQUITO


def test_mb_mosquito_09_boss_design_is_well_formed() -> None:
    """Its parts (wings, proboscis), guns and stage volleys fit together (MB-MOSQUITO-08)."""
    assert_boss_design(MOSQUITO)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert MOSQUITO.id == MOSQUITO.id.lower()
    assert " " not in MOSQUITO.id
    assert "_" not in MOSQUITO.id


def test_mb_mosquito_08_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (MB-MOSQUITO-07)."""
    stats = MOSQUITO.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_mb_mosquito_11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (MB-MOSQUITO-10)."""
    assert isinstance(MOSQUITO.rage, list)
    assert MOSQUITO.rage
    assert len(MOSQUITO.stages) == len(original_parts(MOSQUITO)) + 1
