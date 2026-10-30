"""Unit tests of `src/game/config/bosses/world_3/mosquito.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_3.mosquito import MOSQUITO


def test_p09_r09_boss_design_is_well_formed() -> None:
    assert_boss_design(MOSQUITO)


def test_p09_r09_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert MOSQUITO.id == MOSQUITO.id.lower()
    assert " " not in MOSQUITO.id and "_" not in MOSQUITO.id


def test_p09_r09_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = MOSQUITO.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p09_r09_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(MOSQUITO.rage, list) and MOSQUITO.rage
    assert len(MOSQUITO.stages) == len(MOSQUITO.stats["parts"]) + 1
