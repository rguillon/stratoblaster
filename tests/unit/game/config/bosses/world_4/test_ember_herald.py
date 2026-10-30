"""Unit tests of `src/game/config/bosses/world_4/ember_herald.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_4.ember_herald import EMBER_HERALD


def test_p10_r11_boss_design_is_well_formed() -> None:
    assert_boss_design(EMBER_HERALD)


def test_p10_r11_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert EMBER_HERALD.id == EMBER_HERALD.id.lower()
    assert " " not in EMBER_HERALD.id and "_" not in EMBER_HERALD.id


def test_p10_r11_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = EMBER_HERALD.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p10_r11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(EMBER_HERALD.rage, list) and EMBER_HERALD.rage
    assert len(EMBER_HERALD.stages) == len(EMBER_HERALD.stats["parts"]) + 1
