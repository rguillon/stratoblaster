# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/final_bosses.py`."""

from typing import Any

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
def test_boss_20_final_boss_design_is_well_formed(design: Any) -> None:
    """One stage more than its parts; parts, guns and volleys that fit (BOSS-12, BOSS-23)."""
    assert_boss_design(design)


@pytest.mark.parametrize("design", FINAL_BOSSES, ids=lambda d: d.id)
def test_boss_55_final_boss_is_tougher_than_a_mini_boss(
    design: Any,
) -> None:
    assert design.stats["health"] >= 2000


def test_boss_01_final_bosses_have_distinct_ids() -> None:
    assert len({d.id for d in FINAL_BOSSES}) == len(FINAL_BOSSES)
