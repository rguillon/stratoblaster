"""Unit tests of `src/game/config/bosses/world_2/fjord_lynx.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_2.fjord_lynx import FJORD_LYNX


def test_p08_r10_boss_design_is_well_formed() -> None:
    assert_boss_design(FJORD_LYNX)


def test_p08_r10_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert FJORD_LYNX.id == FJORD_LYNX.id.lower()
    assert " " not in FJORD_LYNX.id and "_" not in FJORD_LYNX.id


def test_p08_r10_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = FJORD_LYNX.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p08_r10_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(FJORD_LYNX.rage, list) and FJORD_LYNX.rage
    assert len(FJORD_LYNX.stages) == len(FJORD_LYNX.stats["parts"]) + 1
