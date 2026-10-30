"""Unit tests of `src/game/config/bosses/world_4/obsidian_golem.py`."""

from helpers.config_checks import assert_boss_design

from game.config.bosses.world_4.obsidian_golem import OBSIDIAN_GOLEM


def test_p10_r11_boss_design_is_well_formed() -> None:
    assert_boss_design(OBSIDIAN_GOLEM)


def test_p10_r11_boss_id_is_a_lowercase_kebab_case_kind() -> None:
    assert OBSIDIAN_GOLEM.id == OBSIDIAN_GOLEM.id.lower()
    assert " " not in OBSIDIAN_GOLEM.id and "_" not in OBSIDIAN_GOLEM.id


def test_p10_r11_boss_stats_are_in_the_range_the_sim_relies_on() -> None:
    stats = OBSIDIAN_GOLEM.stats
    assert 500 <= stats["health"] <= 10000
    assert 0 <= stats["groundSpeed"] <= 2
    assert 0 < stats["coreRadius"] < stats["radius"]


def test_p10_r11_boss_has_an_angry_pattern_and_its_stage_count() -> None:
    assert isinstance(OBSIDIAN_GOLEM.rage, list) and OBSIDIAN_GOLEM.rage
    assert len(OBSIDIAN_GOLEM.stages) == len(OBSIDIAN_GOLEM.stats["parts"]) + 1
