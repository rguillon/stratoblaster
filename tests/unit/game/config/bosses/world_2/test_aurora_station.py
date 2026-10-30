"""Unit tests of `src/game/config/bosses/world_2/aurora_station.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_2.aurora_station import AURORA_STATION


def test_p08_r10_boss_design_is_well_formed() -> None:
    assert_boss_design(AURORA_STATION)


def test_p08_r10_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert AURORA_STATION.id == AURORA_STATION.id.lower()
    assert " " not in AURORA_STATION.id and "_" not in AURORA_STATION.id


def test_p08_r10_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = AURORA_STATION.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p08_r10_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(AURORA_STATION.rage, list) and AURORA_STATION.rage
    assert len(AURORA_STATION.stages) == len(AURORA_STATION.stats["parts"]) + 1
