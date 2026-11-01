"""Unit tests of `src/game/config/bosses/world_2/floe_breaker.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_2.floe_breaker import FLOE_BREAKER


def test_mb_floe_breaker_09_boss_design_is_well_formed() -> None:
    """Its parts (the harpoon guns), guns and stage volleys fit together (MB-FLOE-BREAKER-10)."""
    assert_boss_design(FLOE_BREAKER)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert FLOE_BREAKER.id == FLOE_BREAKER.id.lower()
    assert " " not in FLOE_BREAKER.id and "_" not in FLOE_BREAKER.id


def test_mb_floe_breaker_13_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (MB-FLOE-BREAKER-08)."""
    stats = FLOE_BREAKER.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_mb_floe_breaker_11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (MB-FLOE-BREAKER-10)."""
    assert isinstance(FLOE_BREAKER.rage, list) and FLOE_BREAKER.rage
    assert len(FLOE_BREAKER.stages) == len(original_parts(FLOE_BREAKER)) + 1
