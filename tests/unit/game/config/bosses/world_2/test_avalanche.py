"""Unit tests of `src/game/config/bosses/world_2/avalanche.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_2.avalanche import AVALANCHE


def test_p08_r10_boss_design_is_well_formed() -> None:
    assert_boss_design(AVALANCHE)


def test_p08_r10_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert AVALANCHE.id == AVALANCHE.id.lower()
    assert " " not in AVALANCHE.id and "_" not in AVALANCHE.id


def test_p08_r10_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = AVALANCHE.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p08_r10_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(AVALANCHE.rage, list) and AVALANCHE.rage
    assert len(AVALANCHE.stages) == len(AVALANCHE.stats["parts"]) + 1
