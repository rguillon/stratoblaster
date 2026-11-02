# Copyright (c) 2026 Renaud Guillon
"""A level the player can fly (GAME-LEVEL-16)."""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from core.scenery.scenery_level import SceneryLevel
from core.systems.boss_fights import LevelBoss
from core.systems.enemy_world import EnemyDifficulty
from core.systems.wave_runner import WaveScript

# __pragma__ ("noskip")


class GameLevel:
    """A level the player can fly: its ground.

    Its wave script and how hard its enemies are As data the engine runs (ENG-149).
    """

    def __init__(
        self,
        id_: str,
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
        self.id = id_
        self.scenery = scenery
        self.waves = waves
        self.difficulty = difficulty
        self.bosses = bosses
        self.runout = runout


def find_game_level(levels: list[GameLevel], item_id: str) -> GameLevel | None:
    """Return the level with the given id, or None."""
    for level in levels:
        if level.id == item_id:
            return level
    return None
