"""Unit tests of `src/game/config/bosses/world_4/ash_wraith.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_4.ash_wraith import ASH_WRAITH


def test_p10_r11_boss_design_is_well_formed() -> None:
    assert_boss_design(ASH_WRAITH)


def test_p10_r11_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert ASH_WRAITH.id == ASH_WRAITH.id.lower()
    assert " " not in ASH_WRAITH.id and "_" not in ASH_WRAITH.id


def test_p10_r11_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = ASH_WRAITH.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p10_r11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(ASH_WRAITH.rage, list) and ASH_WRAITH.rage
    assert len(ASH_WRAITH.stages) == len(ASH_WRAITH.stats["parts"]) + 1
