# Copyright (c) 2026 Renaud Guillon
"""World 1 (WLD-1-01): five levels of about 4 minutes."""

from core.content.game_level import GameLevel
from game.config.world_1.bosses import WORLD_1_BOSSES
from game.config.world_1.difficulty import WORLD_1_DIFFICULTY
from game.config.world_1.scenery_coast import LEVEL_1_1, LEVEL_1_2
from game.config.world_1.scenery_country import LEVEL_1_3
from game.config.world_1.scenery_desert import LEVEL_1_4, LEVEL_1_5
from game.config.world_1.waves import (
    WAVES_1_1,
    WAVES_1_2,
    WAVES_1_3,
    WAVES_1_4,
    WAVES_1_5,
    WORLD_1_FILLERS,
)
from game.sim.assemble_level import WorldTables, assemble_level

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# A beat is a config record (`game/config/record.py`), typed as Any there.
Beat = Any
# __pragma__ ("noskip")


TABLES = WorldTables(WORLD_1_DIFFICULTY, WORLD_1_FILLERS, WORLD_1_BOSSES)


def _level(level_id: str, scenery: Any, beats: list[Beat]) -> GameLevel:
    return assemble_level(level_id, scenery, beats, TABLES)


# World 1: five levels of about 4 minutes, from the open sea over green grassland to the deep
# desert, each with a mini boss and a final boss (WLD-1-26).
WORLD_1 = [
    _level("1-1", LEVEL_1_1, WAVES_1_1),  # LVL-1-1-01
    _level("1-2", LEVEL_1_2, WAVES_1_2),  # LVL-1-2-01
    _level("1-3", LEVEL_1_3, WAVES_1_3),  # LVL-1-3-01
    _level("1-4", LEVEL_1_4, WAVES_1_4),  # LVL-1-4-01
    _level("1-5", LEVEL_1_5, WAVES_1_5),  # LVL-1-5-01
]
