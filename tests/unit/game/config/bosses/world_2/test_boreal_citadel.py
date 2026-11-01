"""Unit tests of `src/game/config/bosses/world_2/boreal_citadel.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_2.boreal_citadel import BOREAL_CITADEL


def test_fb_boreal_citadel_10_boss_design_is_well_formed() -> None:
    """Its parts (aurora cannons, missile batteries FB-BOREAL-CITADEL-11, dome generators
    FB-BOREAL-CITADEL-12), guns and stage volleys fit together (FB-BOREAL-CITADEL-13)."""
    assert_boss_design(BOREAL_CITADEL)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert BOREAL_CITADEL.id == BOREAL_CITADEL.id.lower()
    assert " " not in BOREAL_CITADEL.id and "_" not in BOREAL_CITADEL.id


def test_fb_boreal_citadel_17_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-BOREAL-CITADEL-09)."""
    stats = BOREAL_CITADEL.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_boreal_citadel_14_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (FB-BOREAL-CITADEL-13)."""
    assert isinstance(BOREAL_CITADEL.rage, list) and BOREAL_CITADEL.rage
    assert len(BOREAL_CITADEL.stages) == len(original_parts(BOREAL_CITADEL)) + 1
