"""Unit tests of `src/game/config/bosses/world_4/magma_salamander.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_4.magma_salamander import MAGMA_SALAMANDER


def test_p10_r11_boss_design_is_well_formed() -> None:
    assert_boss_design(MAGMA_SALAMANDER)


def test_p10_r11_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert MAGMA_SALAMANDER.id == MAGMA_SALAMANDER.id.lower()
    assert " " not in MAGMA_SALAMANDER.id and "_" not in MAGMA_SALAMANDER.id


def test_p10_r11_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = MAGMA_SALAMANDER.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p10_r11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(MAGMA_SALAMANDER.rage, list) and MAGMA_SALAMANDER.rage
    assert len(MAGMA_SALAMANDER.stages) == len(MAGMA_SALAMANDER.stats["parts"]) + 1
