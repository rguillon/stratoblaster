"""Unit tests of `src/game/config/bosses/world_2/ice_queen.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_2.ice_queen import ICE_QUEEN


def test_p08_r10_boss_design_is_well_formed() -> None:
    assert_boss_design(ICE_QUEEN)


def test_p08_r10_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert ICE_QUEEN.id == ICE_QUEEN.id.lower()
    assert " " not in ICE_QUEEN.id and "_" not in ICE_QUEEN.id


def test_p08_r10_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = ICE_QUEEN.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p08_r10_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(ICE_QUEEN.rage, list) and ICE_QUEEN.rage
    assert len(ICE_QUEEN.stages) == len(ICE_QUEEN.stats["parts"]) + 1
