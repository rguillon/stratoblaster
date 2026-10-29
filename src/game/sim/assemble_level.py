"""A playable level from its scenery and its written beats (P06, P07, P08), ported from
`game/sim/assemble-level.ts`.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.content.game_level import GameLevel
from core.scenery.scenery_level import level_length
from core.systems.boss_fights import LevelBoss
from game.config.world_1.bosses import MINI_BOSS_AT, QUIET_BEFORE_BOSS
from game.config.world_1.waves import fill, quiet_before, wave_script

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from core.scenery.scenery_level import SceneryLevel  # noqa: E402
from core.systems.enemy_world import EnemyDifficulty  # noqa: E402

__pragma__("noskip")

# Config records (`game/config/record.py`), typed as Any there: a level's beats, its filler and
# its bosses.
__pragma__("skip")
Beat = Any
__pragma__("noskip")
__pragma__("skip")
Filler = Any
__pragma__("noskip")
__pragma__("skip")
LevelBosses = Any
__pragma__("noskip")


class WorldTables:
    """What a world gives each of its levels, by level id: its difficulty, its filler and its
    bosses (`dict`s keyed by the level id).
    """

    def __init__(
        self,
        difficulty: dict[str, EnemyDifficulty],
        fillers: dict[str, Filler],
        bosses: dict[str, LevelBosses],
    ) -> None:
        self.difficulty = difficulty
        self.fillers = fillers
        self.bosses = bosses


def assemble_level(
    id: str,
    scenery: SceneryLevel,
    beats: list[Beat],
    tables: WorldTables,
) -> GameLevel:
    """A playable level (P06, P07, P08): its scenery, its written beats with light groups filling
    their lulls (phase 6 review) and nothing new in the stretch before each boss (P07-R06), its
    difficulty, and its mini boss at the middle and final boss at the end.
    """
    difficulty = tables.difficulty.get(id)
    filler = tables.fillers.get(id)
    bosses = tables.bosses.get(id)
    if difficulty is None or filler is None or bosses is None:
        raise ValueError('No difficulty, filler or boss for "' + id + '"')
    length = level_length(scenery)
    raw: Any = scenery  # a game/config record: camelCase keys
    fights = [
        LevelBoss(bosses.mini, "mini", length * MINI_BOSS_AT),
        LevelBoss(bosses.final, "final", length),
    ]
    script = wave_script(raw.scrollSpeed, fill(beats, filler))
    quiet = QUIET_BEFORE_BOSS * raw.scrollSpeed
    waves = quiet_before(script, [fight.at for fight in fights], quiet)
    return GameLevel(id, scenery, waves, difficulty, fights, bosses.runout)
