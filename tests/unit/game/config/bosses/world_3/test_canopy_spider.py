"""Unit tests of `src/game/config/bosses/world_3/canopy_spider.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_3.canopy_spider import CANOPY_SPIDER


def test_p09_r09_boss_design_is_well_formed() -> None:
    assert_boss_design(CANOPY_SPIDER)


def test_p09_r09_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert CANOPY_SPIDER.id == CANOPY_SPIDER.id.lower()
    assert " " not in CANOPY_SPIDER.id and "_" not in CANOPY_SPIDER.id


def test_p09_r09_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = CANOPY_SPIDER.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p09_r09_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(CANOPY_SPIDER.rage, list) and CANOPY_SPIDER.rage
    assert len(CANOPY_SPIDER.stages) == len(CANOPY_SPIDER.stats["parts"]) + 1
