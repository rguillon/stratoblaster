# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_4/ember_herald.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_4.ember_herald import EMBER_HERALD


def test_mb_ember_herald_08_boss_design_is_well_formed() -> None:
    """Its parts (the lances), guns and stage volleys fit together (MB-EMBER-HERALD-09)."""
    assert_boss_design(EMBER_HERALD)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert EMBER_HERALD.id == EMBER_HERALD.id.lower()
    assert " " not in EMBER_HERALD.id
    assert "_" not in EMBER_HERALD.id


def test_mb_ember_herald_07_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (MB-EMBER-HERALD-05)."""
    stats = EMBER_HERALD.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_mb_ember_herald_10_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (MB-EMBER-HERALD-09)."""
    assert isinstance(EMBER_HERALD.rage, list)
    assert EMBER_HERALD.rage
    assert len(EMBER_HERALD.stages) == len(original_parts(EMBER_HERALD)) + 1
