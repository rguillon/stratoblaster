"""Unit tests of `src/game/config/bosses/world_3/toucan.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_3.toucan import TOUCAN


def test_p09_r09_boss_design_is_well_formed() -> None:
    assert_boss_design(TOUCAN)


def test_p09_r09_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert TOUCAN.id == TOUCAN.id.lower()
    assert " " not in TOUCAN.id and "_" not in TOUCAN.id


def test_p09_r09_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = TOUCAN.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p09_r09_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(TOUCAN.rage, list) and TOUCAN.rage
    assert len(TOUCAN.stages) == len(TOUCAN.stats["parts"]) + 1
