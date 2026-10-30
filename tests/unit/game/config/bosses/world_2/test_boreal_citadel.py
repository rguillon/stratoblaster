"""Unit tests of `src/game/config/bosses/world_2/boreal_citadel.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_2.boreal_citadel import BOREAL_CITADEL


def test_p08_r10_boss_design_is_well_formed() -> None:
    assert_boss_design(BOREAL_CITADEL)


def test_p08_r10_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert BOREAL_CITADEL.id == BOREAL_CITADEL.id.lower()
    assert " " not in BOREAL_CITADEL.id and "_" not in BOREAL_CITADEL.id


def test_p08_r10_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = BOREAL_CITADEL.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p08_r10_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(BOREAL_CITADEL.rage, list) and BOREAL_CITADEL.rage
    assert len(BOREAL_CITADEL.stages) == len(BOREAL_CITADEL.stats["parts"]) + 1
