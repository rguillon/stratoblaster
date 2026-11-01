# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_2/snow_owl.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_2.snow_owl import SNOW_OWL


def test_mb_snow_owl_09_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together.

    Parts: wing radar pods, sensor eye (MB-SNOW-OWL-10). Guns and stage volleys: MB-SNOW-OWL-11.
    """
    assert_boss_design(SNOW_OWL)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert SNOW_OWL.id == SNOW_OWL.id.lower()
    assert " " not in SNOW_OWL.id
    assert "_" not in SNOW_OWL.id


def test_mb_snow_owl_14_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (MB-SNOW-OWL-08)."""
    stats = SNOW_OWL.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_mb_snow_owl_12_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (MB-SNOW-OWL-11)."""
    assert isinstance(SNOW_OWL.rage, list)
    assert SNOW_OWL.rage
    assert len(SNOW_OWL.stages) == len(original_parts(SNOW_OWL)) + 1
