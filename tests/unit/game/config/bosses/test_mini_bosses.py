"""Unit tests of `src/game/config/bosses/mini_bosses.py`."""

import pytest
from helpers.config_checks import assert_boss_design

from game.config.bosses.mini_bosses import BREAKWATER, DUST_DEVIL, REEF_WARDEN, SCORPION, SENTINEL

MINI_BOSSES = [REEF_WARDEN, BREAKWATER, DUST_DEVIL, SCORPION, SENTINEL]


@pytest.mark.parametrize("design", MINI_BOSSES, ids=lambda d: d.id)
def test_p07_r05_mini_boss_design_is_well_formed(design) -> None:
    assert_boss_design(design)


@pytest.mark.parametrize("design", MINI_BOSSES, ids=lambda d: d.id)
def test_p07_r05_mini_boss_is_weaker_than_the_final_boss_of_its_level(design) -> None:
    assert design.stats["health"] < 2500
    assert design.rage


def test_p07_r05_mini_bosses_have_distinct_ids() -> None:
    assert len({d.id for d in MINI_BOSSES}) == len(MINI_BOSSES)
