"""Unit tests of `src/game/config/bosses/world_4/geyser_rig.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_4.geyser_rig import GEYSER_RIG


def test_p10_r11_boss_design_is_well_formed() -> None:
    assert_boss_design(GEYSER_RIG)


def test_p10_r11_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert GEYSER_RIG.id == GEYSER_RIG.id.lower()
    assert " " not in GEYSER_RIG.id and "_" not in GEYSER_RIG.id


def test_p10_r11_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = GEYSER_RIG.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p10_r11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(GEYSER_RIG.rage, list) and GEYSER_RIG.rage
    assert len(GEYSER_RIG.stages) == len(GEYSER_RIG.stats["parts"]) + 1
