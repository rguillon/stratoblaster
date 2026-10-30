"""A playable level from its scenery and its written beats (P06, P07, P08)"""

from org.transcrypt.stubs.browser import __pragma__

from core.content.game_level import GameLevel
from core.scenery.scenery_level import level_length
from core.systems.boss_fights import LevelBoss
from core.systems.enemy_world import EnemyDifficulty
from game.config.world_1.bosses import MINI_BOSS_AT, QUIET_BEFORE_BOSS
from game.config.world_1.waves import fill, quiet_before, wave_script
from game.sim.scenery_build import scenery_level

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# Config records (`game/config/record.py`), typed as Any there: a level's scenery, beats, filler,
# difficulty and bosses.
__pragma__("skip")
Beat = Any
Filler = Any
LevelBosses = Any
Difficulty = Any
ScenerySource = Any
__pragma__("noskip")


class WorldTables:
    """What a world gives each of its levels, by level id: its difficulty, its filler and its
    bosses (`dict`s keyed by the level id).
    """

    def __init__(
        self,
        difficulty: dict[str, Difficulty],
        fillers: dict[str, Filler],
        bosses: dict[str, LevelBosses],
    ) -> None:
        self.difficulty = difficulty
        self.fillers = fillers
        self.bosses = bosses


def _difficulty(config: Difficulty) -> EnemyDifficulty:
    """A level's enemy difficulty, as `core/` reads it (P06-R08)."""
    return EnemyDifficulty(config.bulletSpeed, config.fireRate)


def assemble_level(
    id: str,
    scenery: ScenerySource,
    beats: list[Beat],
    tables: WorldTables,
) -> GameLevel:
    """A playable level (P06, P07, P08): its scenery (`scenery` is its config record, mapped to the
    core's `SceneryLevel` here), its written beats with light groups filling their lulls (phase 6
    review) and nothing new in the stretch before each boss (P07-R06), its difficulty, and its mini
    boss at the middle and final boss at the end.
    """
    difficulty_config = tables.difficulty.get(id)
    filler = tables.fillers.get(id)
    bosses = tables.bosses.get(id)
    if difficulty_config is None or filler is None or bosses is None:
        raise ValueError('No difficulty, filler or boss for "' + id + '"')
    level = scenery_level(scenery)
    length = level_length(level)
    fights = [
        LevelBoss(bosses.mini, "mini", length * MINI_BOSS_AT),
        LevelBoss(bosses.final, "final", length),
    ]
    script = wave_script(scenery.scrollSpeed, fill(beats, filler))
    quiet = QUIET_BEFORE_BOSS * scenery.scrollSpeed
    waves = quiet_before(script, [fight.at for fight in fights], quiet)
    return GameLevel(
        id,
        level,
        waves,
        _difficulty(difficulty_config),
        fights,
        bosses.runout,
    )
