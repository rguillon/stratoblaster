"""Unit tests of `src/game/config/bosses/world_3/mangrove_croc.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_3.mangrove_croc import MANGROVE_CROC


def test_p09_r09_boss_design_is_well_formed() -> None:
    assert_boss_design(MANGROVE_CROC)


def test_p09_r09_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert MANGROVE_CROC.id == MANGROVE_CROC.id.lower()
    assert " " not in MANGROVE_CROC.id and "_" not in MANGROVE_CROC.id


def test_p09_r09_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = MANGROVE_CROC.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p09_r09_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(MANGROVE_CROC.rage, list) and MANGROVE_CROC.rage
    assert len(MANGROVE_CROC.stages) == len(MANGROVE_CROC.stats["parts"]) + 1
