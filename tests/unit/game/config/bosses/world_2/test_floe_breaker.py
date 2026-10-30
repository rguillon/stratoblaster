"""Unit tests of `src/game/config/bosses/world_2/floe_breaker.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_2.floe_breaker import FLOE_BREAKER


def test_p08_r10_boss_design_is_well_formed() -> None:
    assert_boss_design(FLOE_BREAKER)


def test_p08_r10_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert FLOE_BREAKER.id == FLOE_BREAKER.id.lower()
    assert " " not in FLOE_BREAKER.id and "_" not in FLOE_BREAKER.id


def test_p08_r10_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = FLOE_BREAKER.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p08_r10_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(FLOE_BREAKER.rage, list) and FLOE_BREAKER.rage
    assert len(FLOE_BREAKER.stages) == len(FLOE_BREAKER.stats["parts"]) + 1
