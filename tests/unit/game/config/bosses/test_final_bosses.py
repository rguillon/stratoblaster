"""Unit tests of `src/game/config/bosses/final_bosses.py`."""

import pytest
from helpers.config_checks import assert_boss_design

from game.config.bosses.final_bosses import (
    GULL_MOTHERSHIP,
    MESA_FORTRESS,
    OVERLORD,
    REFINERY_TITAN,
    STORM_PETREL,
)

FINAL_BOSSES = [STORM_PETREL, GULL_MOTHERSHIP, MESA_FORTRESS, REFINERY_TITAN, OVERLORD]


@pytest.mark.parametrize("design", FINAL_BOSSES, ids=lambda d: d.id)
def test_p07_r05_final_boss_design_is_well_formed(design) -> None:
    assert_boss_design(design)


@pytest.mark.parametrize("design", FINAL_BOSSES, ids=lambda d: d.id)
def test_p07_r05_final_boss_is_tougher_than_a_mini_boss_and_has_an_angry_pattern(design) -> None:
    assert design.stats["health"] >= 2000
    assert design.rage


def test_p07_r05_final_bosses_have_distinct_ids() -> None:
    assert len({d.id for d in FINAL_BOSSES}) == len(FINAL_BOSSES)
