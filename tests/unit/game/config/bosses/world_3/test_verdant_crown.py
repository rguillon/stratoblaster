"""Unit tests of `src/game/config/bosses/world_3/verdant_crown.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_3.verdant_crown import VERDANT_CROWN


def test_p09_r09_boss_design_is_well_formed() -> None:
    assert_boss_design(VERDANT_CROWN)


def test_p09_r09_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert VERDANT_CROWN.id == VERDANT_CROWN.id.lower()
    assert " " not in VERDANT_CROWN.id and "_" not in VERDANT_CROWN.id


def test_p09_r09_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = VERDANT_CROWN.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p09_r09_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(VERDANT_CROWN.rage, list) and VERDANT_CROWN.rage
    assert len(VERDANT_CROWN.stages) == len(VERDANT_CROWN.stats["parts"]) + 1
