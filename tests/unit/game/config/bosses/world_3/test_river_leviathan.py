"""Unit tests of `src/game/config/bosses/world_3/river_leviathan.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_3.river_leviathan import RIVER_LEVIATHAN


def test_p09_r09_boss_design_is_well_formed() -> None:
    assert_boss_design(RIVER_LEVIATHAN)


def test_p09_r09_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert RIVER_LEVIATHAN.id == RIVER_LEVIATHAN.id.lower()
    assert " " not in RIVER_LEVIATHAN.id and "_" not in RIVER_LEVIATHAN.id


def test_p09_r09_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = RIVER_LEVIATHAN.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p09_r09_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(RIVER_LEVIATHAN.rage, list) and RIVER_LEVIATHAN.rage
    assert len(RIVER_LEVIATHAN.stages) == len(RIVER_LEVIATHAN.stats["parts"]) + 1
