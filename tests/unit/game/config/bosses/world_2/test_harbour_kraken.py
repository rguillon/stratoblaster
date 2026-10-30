"""Unit tests of `src/game/config/bosses/world_2/harbour_kraken.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_2.harbour_kraken import HARBOUR_KRAKEN


def test_p08_r10_boss_design_is_well_formed() -> None:
    assert_boss_design(HARBOUR_KRAKEN)


def test_p08_r10_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert HARBOUR_KRAKEN.id == HARBOUR_KRAKEN.id.lower()
    assert " " not in HARBOUR_KRAKEN.id and "_" not in HARBOUR_KRAKEN.id


def test_p08_r10_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = HARBOUR_KRAKEN.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p08_r10_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(HARBOUR_KRAKEN.rage, list) and HARBOUR_KRAKEN.rage
    assert len(HARBOUR_KRAKEN.stages) == len(HARBOUR_KRAKEN.stats["parts"]) + 1
