# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_3/verdant_crown.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_3.verdant_crown import VERDANT_CROWN


def test_fb_verdant_crown_09_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together (FB-VERDANT-CROWN-08)."""
    assert_boss_design(VERDANT_CROWN)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert VERDANT_CROWN.id == VERDANT_CROWN.id.lower()
    assert " " not in VERDANT_CROWN.id
    assert "_" not in VERDANT_CROWN.id


def test_fb_verdant_crown_08_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-VERDANT-CROWN-07)."""
    stats = VERDANT_CROWN.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_verdant_crown_11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (FB-VERDANT-CROWN-10)."""
    assert isinstance(VERDANT_CROWN.rage, list)
    assert VERDANT_CROWN.rage
    assert len(VERDANT_CROWN.stages) == len(original_parts(VERDANT_CROWN)) + 1
