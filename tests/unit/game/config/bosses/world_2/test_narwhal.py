"""Unit tests of `src/game/config/bosses/world_2/narwhal.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_2.narwhal import NARWHAL


def test_p08_r10_boss_design_is_well_formed() -> None:
    assert_boss_design(NARWHAL)


def test_p08_r10_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert NARWHAL.id == NARWHAL.id.lower()
    assert " " not in NARWHAL.id and "_" not in NARWHAL.id


def test_p08_r10_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = NARWHAL.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p08_r10_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(NARWHAL.rage, list) and NARWHAL.rage
    assert len(NARWHAL.stages) == len(NARWHAL.stats["parts"]) + 1
