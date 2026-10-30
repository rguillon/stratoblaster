"""Unit tests of `src/game/config/bosses/world_2/glacier_colossus.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_2.glacier_colossus import GLACIER_COLOSSUS


def test_p08_r10_boss_design_is_well_formed() -> None:
    assert_boss_design(GLACIER_COLOSSUS)


def test_p08_r10_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert GLACIER_COLOSSUS.id == GLACIER_COLOSSUS.id.lower()
    assert " " not in GLACIER_COLOSSUS.id and "_" not in GLACIER_COLOSSUS.id


def test_p08_r10_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = GLACIER_COLOSSUS.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p08_r10_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(GLACIER_COLOSSUS.rage, list) and GLACIER_COLOSSUS.rage
    assert len(GLACIER_COLOSSUS.stages) == len(GLACIER_COLOSSUS.stats["parts"]) + 1
