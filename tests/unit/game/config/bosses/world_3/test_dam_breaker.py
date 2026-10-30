"""Unit tests of `src/game/config/bosses/world_3/dam_breaker.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_3.dam_breaker import DAM_BREAKER


def test_p09_r09_boss_design_is_well_formed() -> None:
    assert_boss_design(DAM_BREAKER)


def test_p09_r09_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert DAM_BREAKER.id == DAM_BREAKER.id.lower()
    assert " " not in DAM_BREAKER.id and "_" not in DAM_BREAKER.id


def test_p09_r09_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = DAM_BREAKER.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p09_r09_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(DAM_BREAKER.rage, list) and DAM_BREAKER.rage
    assert len(DAM_BREAKER.stages) == len(DAM_BREAKER.stats["parts"]) + 1
