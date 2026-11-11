# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/assemble_level.py`."""

import pytest

from core.scenery.scenery_level import level_length
from game.config.wave_plans import level_plan
from game.config.world_1.bosses import MINI_BOSS_AT, QUIET_BEFORE_BOSS, WORLD_1_BOSSES
from game.config.world_1.scenery_coast import LEVEL_1_1
from game.config.world_1.waves import PLAN_1_1, WORLD_1_FILLERS
from game.sim.assemble_level import WorldTables, assemble_level, plan_beats, ships_of
from game.sim.scenery_build import scenery_level

TABLES = WorldTables(WORLD_1_FILLERS, WORLD_1_BOSSES)


def test_game_level_16_a_level_is_assembled_with_its_scenery_and_two_bosses() -> None:
    """Also GAME-LEVEL-04: its two bosses."""
    level = assemble_level("1-1", LEVEL_1_1, PLAN_1_1, TABLES)
    assert level.id == "1-1"
    assert len(level.bosses) == 2
    assert [fight.rank for fight in level.bosses] == ["mini", "final"]
    assert level.runout == WORLD_1_BOSSES["1-1"]["runout"]


def test_game_level_04_the_mini_boss_comes_at_the_middle_and_the_final_boss_at_the_end() -> None:
    level = assemble_level("1-1", LEVEL_1_1, PLAN_1_1, TABLES)
    length = level_length(scenery_level(LEVEL_1_1))
    mini, final = level.bosses
    assert mini.at == pytest.approx(length * MINI_BOSS_AT)
    assert final.at == pytest.approx(length)


def test_game_level_05_no_wave_starts_in_the_quiet_stretch_before_a_boss() -> None:
    level = assemble_level("1-1", LEVEL_1_1, PLAN_1_1, TABLES)
    quiet = QUIET_BEFORE_BOSS * LEVEL_1_1.scrollSpeed
    for fight in level.bosses:
        for wave in level.waves:
            assert not (fight.at - quiet < wave["at"] <= fight.at)


def test_game_level_16_a_level_without_its_filler_or_bosses_is_an_error() -> None:
    lonely = WorldTables({}, WORLD_1_BOSSES)
    with pytest.raises(ValueError, match='No filler or boss for "1-1"'):
        assemble_level("1-1", LEVEL_1_1, PLAN_1_1, lonely)


def test_d_307_every_level_s_enemies_and_bosses_fire_and_fly_as_tuned() -> None:
    level = assemble_level("1-2", LEVEL_1_1, PLAN_1_1, TABLES)
    assert level.difficulty.bullet_speed == 1
    assert level.difficulty.fire_rate == 1


def test_game_level_05_the_plan_is_composed_around_the_quiet_stretches() -> None:
    """D-283: no beat is written there, so none is dropped (every kind it brings is met)."""
    level = assemble_level("1-1", LEVEL_1_1, PLAN_1_1, TABLES)
    beats = plan_beats(PLAN_1_1, LEVEL_1_1, level.bosses)
    for fight in level.bosses:
        end = fight.at / LEVEL_1_1.scrollSpeed
        assert not any(end - QUIET_BEFORE_BOSS - 0.1 < beat[0] <= end + 0.1 for beat in beats)
    written = {beat[1] for beat in beats}
    assert {wave["kind"] for wave in level.waves} == written


def test_d_309_a_level_as_composed_keeps_its_drop_chances() -> None:
    level = assemble_level("1-1", LEVEL_1_1, level_plan(1, 1, 1), TABLES)
    assert level.bonus_scale == 1


@pytest.mark.parametrize("enemies", [0.5, 2.0])
def test_d_309_more_or_fewer_enemies_drop_as_many_bonuses(enemies: float) -> None:
    """The ships times the scale are the ships as composed: as many drops, on average."""
    composed = assemble_level("1-1", LEVEL_1_1, level_plan(1, 1, 1), TABLES)
    level = assemble_level("1-1", LEVEL_1_1, level_plan(1, 1, enemies), TABLES)
    assert ships_of(level.waves) != ships_of(composed.waves)
    assert ships_of(level.waves) * level.bonus_scale == pytest.approx(ships_of(composed.waves))
    assert (level.bonus_scale < 1) == (enemies > 1)


@pytest.mark.parametrize("enemies", [0.5, 2.0, 3.0])
def test_d_307_the_factor_multiplies_each_wave_s_groups_and_keeps_its_time(enemies: float) -> None:
    """The same waves, at the same times, of the same kinds, about `enemies` times the ships."""
    composed = assemble_level("1-2", LEVEL_1_1, level_plan(1, 2, 1), TABLES)
    level = assemble_level("1-2", LEVEL_1_1, level_plan(1, 2, enemies), TABLES)
    assert [(w["at"], w["kind"]) for w in level.waves] == [
        (w["at"], w["kind"]) for w in composed.waves
    ]
    ratio = ships_of(level.waves) / ships_of(composed.waves)
    assert ratio == pytest.approx(enemies, rel=0.2)
