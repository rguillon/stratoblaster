"""Unit tests of `src/game/config/bosses/world_3/sky_temple.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_3.sky_temple import SKY_TEMPLE


def test_p09_r09_boss_design_is_well_formed() -> None:
    assert_boss_design(SKY_TEMPLE)


def test_p09_r09_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert SKY_TEMPLE.id == SKY_TEMPLE.id.lower()
    assert " " not in SKY_TEMPLE.id and "_" not in SKY_TEMPLE.id


def test_p09_r09_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = SKY_TEMPLE.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p09_r09_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(SKY_TEMPLE.rage, list) and SKY_TEMPLE.rage
    assert len(SKY_TEMPLE.stages) == len(SKY_TEMPLE.stats["parts"]) + 1
