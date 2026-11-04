# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_2/fjord_lynx.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_2.fjord_lynx import FJORD_LYNX


def test_mb_fjord_lynx_08_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together.

    Parts: paw cannons, radar mast (MB-FJORD-LYNX-09). Guns and stage volleys: MB-FJORD-LYNX-10.
    """
    assert_boss_design(FJORD_LYNX)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert FJORD_LYNX.id == FJORD_LYNX.id.lower()
    assert " " not in FJORD_LYNX.id
    assert "_" not in FJORD_LYNX.id


def test_mb_fjord_lynx_13_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (MB-FJORD-LYNX-07)."""
    stats = FJORD_LYNX.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_mb_fjord_lynx_11_boss_has_its_stage_count() -> None:
    """One stage pattern more than its parts (MB-FJORD-LYNX-10)."""
    assert len(FJORD_LYNX.stages) == len(original_parts(FJORD_LYNX)) + 1
