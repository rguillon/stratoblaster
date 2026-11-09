# Copyright (c) 2026 Renaud Guillon
"""A playable level from its scenery and its written beats (GAME-LEVEL-16)."""

from core.content.game_level import GameLevel
from core.scenery.scenery_level import level_length
from core.systems.boss_fights import LevelBoss
from core.systems.enemy_world import EnemyDifficulty
from game.config.wave_plans import compose_beats
from game.config.world_1.bosses import MINI_BOSS_AT, QUIET_BEFORE_BOSS
from game.config.world_1.waves import fill, quiet_before, wave_script
from game.sim.scenery_build import scenery_level

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# Config records (`game/config/record.py`), typed as Any there: a level's scenery, beats, filler
# and bosses.
Beat = Any
WavePlan = Any
Filler = Any
LevelBosses = Any
ScenerySource = Any
# __pragma__ ("noskip")


class WorldTables:
    """What a world gives each of its levels: its filler and its bosses (keyed by level id)."""

    def __init__(self, fillers: dict[str, Filler], bosses: dict[str, LevelBosses]) -> None:
        self.fillers = fillers
        self.bosses = bosses


# Every enemy and boss fires and flies as tuned, in every level: a level is harder only by how
# many enemies it brings (`LEVEL_ENEMIES`, D-307).
AS_TUNED = EnemyDifficulty(1, 1)


def plan_beats(plan: WavePlan, scenery: ScenerySource, fights: list[LevelBoss]) -> list[Beat]:
    """Return the beats of `plan`, none in the quiet stretch before a boss (GAME-LEVEL-05).

    The composer skips those stretches rather than the level dropping its beats there, so every
    kind it brings in is met (ENM-50, D-283).
    """
    speed = scenery.scrollSpeed
    quiet = [[fight.at / speed - QUIET_BEFORE_BOSS, fight.at / speed] for fight in fights]
    return compose_beats(plan, quiet)


def assemble_level(
    level_id: str,
    scenery: ScenerySource,
    plan: WavePlan,
    tables: WorldTables,
) -> GameLevel:
    """Return a playable level, as data (GAME-LEVEL-16).

    Its scenery (`scenery` is its config record, mapped to the core's `SceneryLevel` here), its
    written beats with light groups filling their lulls (WLD-1-21) and nothing new in the stretch
    before each boss (GAME-LEVEL-05), and its mini boss at the middle and final boss
    at the end (GAME-LEVEL-04), then its runout. Which bosses and runout are each level's own (the
    "Mini boss", "Final boss" and "Runout" of each level file in `specs/worlds/`).
    """
    filler = tables.fillers.get(level_id)
    bosses = tables.bosses.get(level_id)
    if filler is None or bosses is None:
        raise ValueError('No filler or boss for "' + level_id + '"')
    level = scenery_level(scenery)
    length = level_length(level)
    fights = [
        LevelBoss(bosses.mini, "mini", length * MINI_BOSS_AT),
        LevelBoss(bosses.final, "final", length),
    ]
    script = wave_script(scenery.scrollSpeed, fill(plan_beats(plan, scenery, fights), filler))
    quiet = QUIET_BEFORE_BOSS * scenery.scrollSpeed
    waves = quiet_before(script, [fight.at for fight in fights], quiet)
    return GameLevel(
        level_id,
        level,
        waves,
        AS_TUNED,
        fights,
        bosses.runout,
    )
