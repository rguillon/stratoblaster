"""Unit tests of `src/game/config/bosses/world_4/cinder_crab.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_4.cinder_crab import CINDER_CRAB


def test_p10_r11_boss_design_is_well_formed() -> None:
    assert_boss_design(CINDER_CRAB)


def test_p10_r11_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert CINDER_CRAB.id == CINDER_CRAB.id.lower()
    assert " " not in CINDER_CRAB.id and "_" not in CINDER_CRAB.id


def test_p10_r11_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = CINDER_CRAB.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p10_r11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(CINDER_CRAB.rage, list) and CINDER_CRAB.rage
    assert len(CINDER_CRAB.stages) == len(CINDER_CRAB.stats["parts"]) + 1
