"""Unit tests of `src/game/config/bosses/world_4/furnace_drake.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_4.furnace_drake import FURNACE_DRAKE


def test_p10_r11_boss_design_is_well_formed() -> None:
    assert_boss_design(FURNACE_DRAKE)


def test_p10_r11_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert FURNACE_DRAKE.id == FURNACE_DRAKE.id.lower()
    assert " " not in FURNACE_DRAKE.id and "_" not in FURNACE_DRAKE.id


def test_p10_r11_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = FURNACE_DRAKE.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p10_r11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(FURNACE_DRAKE.rage, list) and FURNACE_DRAKE.rage
    assert len(FURNACE_DRAKE.stages) == len(FURNACE_DRAKE.stats["parts"]) + 1
