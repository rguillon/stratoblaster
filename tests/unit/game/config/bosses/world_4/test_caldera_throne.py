"""Unit tests of `src/game/config/bosses/world_4/caldera_throne.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_4.caldera_throne import CALDERA_THRONE


def test_fb_caldera_throne_09_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together (also FB-CALDERA-THRONE-10)."""
    assert_boss_design(CALDERA_THRONE)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert CALDERA_THRONE.id == CALDERA_THRONE.id.lower()
    assert " " not in CALDERA_THRONE.id and "_" not in CALDERA_THRONE.id


def test_fb_caldera_throne_08_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (FB-CALDERA-THRONE-07)."""
    stats = CALDERA_THRONE.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_fb_caldera_throne_13_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (FB-CALDERA-THRONE-11)."""
    assert isinstance(CALDERA_THRONE.rage, list) and CALDERA_THRONE.rage
    assert len(CALDERA_THRONE.stages) == len(original_parts(CALDERA_THRONE)) + 1
