"""Unit tests of `src/game/config/bosses/world_4/steam_dreadnought.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_4.steam_dreadnought import STEAM_DREADNOUGHT


def test_fb_steam_dreadnought_09_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together (also FB-STEAM-DREADNOUGHT-10,
    FB-STEAM-DREADNOUGHT-11, FB-STEAM-DREADNOUGHT-12)."""
    assert_boss_design(STEAM_DREADNOUGHT)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert STEAM_DREADNOUGHT.id == STEAM_DREADNOUGHT.id.lower()
    assert " " not in STEAM_DREADNOUGHT.id and "_" not in STEAM_DREADNOUGHT.id


def test_fb_steam_dreadnought_08_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-STEAM-DREADNOUGHT-07)."""
    stats = STEAM_DREADNOUGHT.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_steam_dreadnought_14_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (FB-STEAM-DREADNOUGHT-12)."""
    assert isinstance(STEAM_DREADNOUGHT.rage, list) and STEAM_DREADNOUGHT.rage
    assert len(STEAM_DREADNOUGHT.stages) == len(original_parts(STEAM_DREADNOUGHT)) + 1
