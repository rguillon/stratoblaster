"""Unit tests of `src/game/config/bosses/world_4/steam_dreadnought.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_4.steam_dreadnought import STEAM_DREADNOUGHT


def test_p10_r11_boss_design_is_well_formed() -> None:
    assert_boss_design(STEAM_DREADNOUGHT)


def test_p10_r11_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert STEAM_DREADNOUGHT.id == STEAM_DREADNOUGHT.id.lower()
    assert " " not in STEAM_DREADNOUGHT.id and "_" not in STEAM_DREADNOUGHT.id


def test_p10_r11_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = STEAM_DREADNOUGHT.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p10_r11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(STEAM_DREADNOUGHT.rage, list) and STEAM_DREADNOUGHT.rage
    assert len(STEAM_DREADNOUGHT.stages) == len(STEAM_DREADNOUGHT.stats["parts"]) + 1
