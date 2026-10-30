"""Unit tests of `src/game/config/bosses/world_3/stone_idol.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_3.stone_idol import STONE_IDOL


def test_p09_r09_boss_design_is_well_formed() -> None:
    assert_boss_design(STONE_IDOL)


def test_p09_r09_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert STONE_IDOL.id == STONE_IDOL.id.lower()
    assert " " not in STONE_IDOL.id and "_" not in STONE_IDOL.id


def test_p09_r09_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = STONE_IDOL.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p09_r09_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(STONE_IDOL.rage, list) and STONE_IDOL.rage
    assert len(STONE_IDOL.stages) == len(STONE_IDOL.stats["parts"]) + 1
