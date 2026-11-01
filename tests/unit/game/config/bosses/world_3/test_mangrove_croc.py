"""Unit tests of `src/game/config/bosses/world_3/mangrove_croc.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_3.mangrove_croc import MANGROVE_CROC


def test_mb_mangrove_croc_09_boss_design_is_well_formed() -> None:
    """Its parts (pontoons, jaw cannon), guns and volleys fit together (MB-MANGROVE-CROC-08)."""
    assert_boss_design(MANGROVE_CROC)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert MANGROVE_CROC.id == MANGROVE_CROC.id.lower()
    assert " " not in MANGROVE_CROC.id and "_" not in MANGROVE_CROC.id


def test_mb_mangrove_croc_08_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (MB-MANGROVE-CROC-07)."""
    stats = MANGROVE_CROC.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_mb_mangrove_croc_12_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (MB-MANGROVE-CROC-11)."""
    assert isinstance(MANGROVE_CROC.rage, list) and MANGROVE_CROC.rage
    assert len(MANGROVE_CROC.stages) == len(original_parts(MANGROVE_CROC)) + 1
