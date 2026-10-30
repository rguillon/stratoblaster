"""Unit tests of `src/game/sim/assemble_level.py`."""

import pytest

from core.scenery.scenery_level import level_length
from game.config.world_1.bosses import MINI_BOSS_AT, QUIET_BEFORE_BOSS, WORLD_1_BOSSES
from game.config.world_1.difficulty import WORLD_1_DIFFICULTY
from game.config.world_1.scenery_coast import LEVEL_1_1
from game.config.world_1.waves import WAVES_1_1, WORLD_1_FILLERS
from game.sim.assemble_level import WorldTables, assemble_level
from game.sim.scenery_build import scenery_level

TABLES = WorldTables(WORLD_1_DIFFICULTY, WORLD_1_FILLERS, WORLD_1_BOSSES)


def test_p06_r08_a_level_is_assembled_with_its_scenery_difficulty_and_two_bosses() -> None:
    level = assemble_level("1-1", LEVEL_1_1, WAVES_1_1, TABLES)
    assert level.id == "1-1"
    assert len(level.bosses) == 2
    assert [fight.rank for fight in level.bosses] == ["mini", "final"]
    assert level.runout == WORLD_1_BOSSES["1-1"]["runout"]


def test_p06_r08_the_mini_boss_comes_at_the_middle_and_the_final_boss_at_the_end() -> None:
    level = assemble_level("1-1", LEVEL_1_1, WAVES_1_1, TABLES)
    length = level_length(scenery_level(LEVEL_1_1))
    mini, final = level.bosses
    assert mini.at == pytest.approx(length * MINI_BOSS_AT)
    assert final.at == pytest.approx(length)


def test_p06_r08_no_wave_starts_in_the_quiet_stretch_before_a_boss() -> None:
    level = assemble_level("1-1", LEVEL_1_1, WAVES_1_1, TABLES)
    quiet = QUIET_BEFORE_BOSS * LEVEL_1_1.scrollSpeed
    for fight in level.bosses:
        for wave in level.waves:
            assert not (fight.at - quiet < wave["at"] <= fight.at)


def test_p06_r08_a_level_without_its_difficulty_filler_or_bosses_is_an_error() -> None:
    lonely = WorldTables({}, WORLD_1_FILLERS, WORLD_1_BOSSES)
    with pytest.raises(ValueError, match='No difficulty, filler or boss for "1-1"'):
        assemble_level("1-1", LEVEL_1_1, WAVES_1_1, lonely)


def test_p06_r08_the_difficulty_of_a_level_becomes_the_enemy_difficulty() -> None:
    level = assemble_level("1-2", LEVEL_1_1, WAVES_1_1, TABLES)
    assert level.difficulty.bullet_speed == WORLD_1_DIFFICULTY["1-2"]["bulletSpeed"]
    assert level.difficulty.fire_rate == WORLD_1_DIFFICULTY["1-2"]["fireRate"]
