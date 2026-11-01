"""Unit tests of `src/game/config/bosses/world_2/ice_queen.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_2.ice_queen import ICE_QUEEN


def test_mb_ice_queen_09_boss_design_is_well_formed() -> None:
    """Its parts (the crystal shards), guns and stage volleys fit together (MB-ICE-QUEEN-10)."""
    assert_boss_design(ICE_QUEEN)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert ICE_QUEEN.id == ICE_QUEEN.id.lower()
    assert " " not in ICE_QUEEN.id and "_" not in ICE_QUEEN.id


def test_mb_ice_queen_13_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (MB-ICE-QUEEN-08)."""
    stats = ICE_QUEEN.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_mb_ice_queen_11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (MB-ICE-QUEEN-10)."""
    assert isinstance(ICE_QUEEN.rage, list) and ICE_QUEEN.rage
    assert len(ICE_QUEEN.stages) == len(original_parts(ICE_QUEEN)) + 1
