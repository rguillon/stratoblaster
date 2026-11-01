"""A level the player can fly (GAME-LEVEL-16)"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.scenery.scenery_level import SceneryLevel  # noqa: E402 (after the Transcrypt skip block, ENG-153)
from core.systems.boss_fights import LevelBoss  # noqa: E402 (after the Transcrypt skip block, ENG-153)
from core.systems.enemy_world import EnemyDifficulty  # noqa: E402 (after the Transcrypt skip block, ENG-153)
from core.systems.wave_runner import WaveScript  # noqa: E402 (after the Transcrypt skip block, ENG-153)

__pragma__("noskip")


class GameLevel:
    """A level the player can fly: its ground, its wave script and how hard its enemies are, as
    data the engine runs (ENG-149).
    """

    def __init__(
        self,
        id: str,
        scenery: SceneryLevel,
        waves: WaveScript,
        difficulty: EnemyDifficulty,
        bosses: list[LevelBoss] | None = None,
        runout: float | None = None,
    ) -> None:
        """`id` is the id of its entry on the level select screen (`LevelEntry.id`).

        - `bosses`: its bosses (GAME-LEVEL-04): a mini boss and a final boss. With a final boss,
          the level ends when it is destroyed; without one, at the end of its scroll
          (GAME-LEVEL-10).
        - `runout`: seconds (at the level's ground speed) of extra ground drawn after the level's
          end, like its last section, for a final boss fight that keeps the ground scrolling
          (GAME-LEVEL-08). Past it, the terrain still goes on.
        """
        self.id = id
        self.scenery = scenery
        self.waves = waves
        self.difficulty = difficulty
        self.bosses = bosses
        self.runout = runout


def find_game_level(levels: list[GameLevel], id: str) -> GameLevel | None:
    """The level with id `id`, or None."""
    for level in levels:
        if level.id == id:
            return level
    return None
