"""Unit tests of `src/game/config/bosses/world_2/snow_owl.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_2.snow_owl import SNOW_OWL


def test_p08_r10_boss_design_is_well_formed() -> None:
    assert_boss_design(SNOW_OWL)


def test_p08_r10_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert SNOW_OWL.id == SNOW_OWL.id.lower()
    assert " " not in SNOW_OWL.id and "_" not in SNOW_OWL.id


def test_p08_r10_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = SNOW_OWL.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p08_r10_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(SNOW_OWL.rage, list) and SNOW_OWL.rage
    assert len(SNOW_OWL.stages) == len(SNOW_OWL.stats["parts"]) + 1
