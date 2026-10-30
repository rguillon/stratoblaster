"""Unit tests of `src/game/config/bosses/world_4/foundry_ark.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_4.foundry_ark import FOUNDRY_ARK


def test_p10_r11_boss_design_is_well_formed() -> None:
    assert_boss_design(FOUNDRY_ARK)


def test_p10_r11_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert FOUNDRY_ARK.id == FOUNDRY_ARK.id.lower()
    assert " " not in FOUNDRY_ARK.id and "_" not in FOUNDRY_ARK.id


def test_p10_r11_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = FOUNDRY_ARK.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p10_r11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(FOUNDRY_ARK.rage, list) and FOUNDRY_ARK.rage
    assert len(FOUNDRY_ARK.stages) == len(FOUNDRY_ARK.stats["parts"]) + 1
