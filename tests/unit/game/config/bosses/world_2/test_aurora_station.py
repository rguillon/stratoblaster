# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bosses/world_2/aurora_station.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_2.aurora_station import AURORA_STATION


def test_fb_aurora_station_09_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together.

    Parts: dish emitters, cryo cannons (FB-AURORA-STATION-10), hangar (FB-AURORA-STATION-11). Guns
    and stage volleys: FB-AURORA-STATION-12.
    """
    assert_boss_design(AURORA_STATION)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert AURORA_STATION.id == AURORA_STATION.id.lower()
    assert " " not in AURORA_STATION.id
    assert "_" not in AURORA_STATION.id


def test_fb_aurora_station_16_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-AURORA-STATION-08)."""
    stats = AURORA_STATION.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_aurora_station_13_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (FB-AURORA-STATION-12)."""
    assert isinstance(AURORA_STATION.rage, list)
    assert AURORA_STATION.rage
    assert len(AURORA_STATION.stages) == len(original_parts(AURORA_STATION)) + 1
