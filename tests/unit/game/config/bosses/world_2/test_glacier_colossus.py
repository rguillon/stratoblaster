# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_2/glacier_colossus.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_2.glacier_colossus import GLACIER_COLOSSUS


def test_fb_glacier_colossus_09_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together.

    Parts: cutters, ore cannons (FB-GLACIER-COLOSSUS-10), heat sink (FB-GLACIER-COLOSSUS-11),
    missile pod (FB-GLACIER-COLOSSUS-12). Guns and stage volleys: FB-GLACIER-COLOSSUS-13.
    """
    assert_boss_design(GLACIER_COLOSSUS)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert GLACIER_COLOSSUS.id == GLACIER_COLOSSUS.id.lower()
    assert " " not in GLACIER_COLOSSUS.id
    assert "_" not in GLACIER_COLOSSUS.id


def test_fb_glacier_colossus_17_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-GLACIER-COLOSSUS-08)."""
    stats = GLACIER_COLOSSUS.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_glacier_colossus_14_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (FB-GLACIER-COLOSSUS-13)."""
    assert isinstance(GLACIER_COLOSSUS.rage, list)
    assert GLACIER_COLOSSUS.rage
    assert len(GLACIER_COLOSSUS.stages) == len(original_parts(GLACIER_COLOSSUS)) + 1
