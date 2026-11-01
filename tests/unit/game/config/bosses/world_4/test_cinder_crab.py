"""Unit tests of `src/game/config/bosses/world_4/cinder_crab.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_4.cinder_crab import CINDER_CRAB


def test_mb_cinder_crab_09_boss_design_is_well_formed() -> None:
    """Its parts (claws, mortar), guns and stage volleys fit together (MB-CINDER-CRAB-10)."""
    assert_boss_design(CINDER_CRAB)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert CINDER_CRAB.id == CINDER_CRAB.id.lower()
    assert " " not in CINDER_CRAB.id and "_" not in CINDER_CRAB.id


def test_mb_cinder_crab_08_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (MB-CINDER-CRAB-07)."""
    stats = CINDER_CRAB.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_mb_cinder_crab_12_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (MB-CINDER-CRAB-11)."""
    assert isinstance(CINDER_CRAB.rage, list) and CINDER_CRAB.rage
    assert len(CINDER_CRAB.stages) == len(original_parts(CINDER_CRAB)) + 1
