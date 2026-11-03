# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_3/canopy_spider.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_3.canopy_spider import CANOPY_SPIDER


def test_fb_canopy_spider_09_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together (FB-CANOPY-SPIDER-08)."""
    assert_boss_design(CANOPY_SPIDER)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert CANOPY_SPIDER.id == CANOPY_SPIDER.id.lower()
    assert " " not in CANOPY_SPIDER.id
    assert "_" not in CANOPY_SPIDER.id


def test_fb_canopy_spider_08_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-CANOPY-SPIDER-07)."""
    stats = CANOPY_SPIDER.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_canopy_spider_11_boss_has_its_stage_count() -> None:
    """One stage pattern more than its parts (FB-CANOPY-SPIDER-10)."""
    assert len(CANOPY_SPIDER.stages) == len(original_parts(CANOPY_SPIDER)) + 1
