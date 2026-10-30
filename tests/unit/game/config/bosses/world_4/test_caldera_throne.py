"""Unit tests of `src/game/config/bosses/world_4/caldera_throne.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_4.caldera_throne import CALDERA_THRONE


def test_p10_r11_boss_design_is_well_formed() -> None:
    assert_boss_design(CALDERA_THRONE)


def test_p10_r11_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert CALDERA_THRONE.id == CALDERA_THRONE.id.lower()
    assert " " not in CALDERA_THRONE.id and "_" not in CALDERA_THRONE.id


def test_p10_r11_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = CALDERA_THRONE.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p10_r11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(CALDERA_THRONE.rage, list) and CALDERA_THRONE.rage
    assert len(CALDERA_THRONE.stages) == len(CALDERA_THRONE.stats["parts"]) + 1
