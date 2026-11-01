"""Unit tests of `src/game/config/bosses/world_4/magma_salamander.py`."""

from helpers.config_checks import assert_boss_design, original_parts

from game.config.bosses.world_4.magma_salamander import MAGMA_SALAMANDER


def test_mb_magma_salamander_09_boss_design_is_well_formed() -> None:
    """Its parts, guns and stage volleys fit together (also MB-MAGMA-SALAMANDER-10)."""
    assert_boss_design(MAGMA_SALAMANDER)


def test_boss_07_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert MAGMA_SALAMANDER.id == MAGMA_SALAMANDER.id.lower()
    assert " " not in MAGMA_SALAMANDER.id and "_" not in MAGMA_SALAMANDER.id


def test_mb_magma_salamander_08_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    """Its health and size, and its fight ground speed (MB-MAGMA-SALAMANDER-07)."""
    stats = MAGMA_SALAMANDER.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_mb_magma_salamander_12_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    """Its rage, and one stage pattern more than its parts (MB-MAGMA-SALAMANDER-11)."""
    assert isinstance(MAGMA_SALAMANDER.rage, list) and MAGMA_SALAMANDER.rage
    assert len(MAGMA_SALAMANDER.stages) == len(original_parts(MAGMA_SALAMANDER)) + 1
