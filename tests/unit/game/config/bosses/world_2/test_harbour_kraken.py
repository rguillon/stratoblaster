# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_2/harbour_kraken.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_2.harbour_kraken import HARBOUR_KRAKEN


def test_fb_harbour_kraken_09_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together.

    Parts: grab cannons, container bay (FB-HARBOUR-KRAKEN-10). Guns and stage volleys: FB-HARBOUR-
    KRAKEN-11.
    """
    assert_boss_design(HARBOUR_KRAKEN)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert HARBOUR_KRAKEN.id == HARBOUR_KRAKEN.id.lower()
    assert " " not in HARBOUR_KRAKEN.id
    assert "_" not in HARBOUR_KRAKEN.id


def test_fb_harbour_kraken_15_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-HARBOUR-KRAKEN-08)."""
    stats = HARBOUR_KRAKEN.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_harbour_kraken_12_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (FB-HARBOUR-KRAKEN-11)."""
    assert isinstance(HARBOUR_KRAKEN.rage, list)
    assert HARBOUR_KRAKEN.rage
    assert len(HARBOUR_KRAKEN.stages) == len(original_parts(HARBOUR_KRAKEN)) + 1
