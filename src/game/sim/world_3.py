"""World 3"""

from org.transcrypt.stubs.browser import __pragma__

from core.content.game_level import GameLevel
from game.config.world_2.waves import compose_beats
from game.config.world_3.bosses import WORLD_3_BOSSES
from game.config.world_3.difficulty import WORLD_3_DIFFICULTY
from game.config.world_3.scenery import LEVEL_3_1, LEVEL_3_2, LEVEL_3_3, LEVEL_3_4, LEVEL_3_5
from game.config.world_3.waves import (
    PLAN_3_1,
    PLAN_3_2,
    PLAN_3_3,
    PLAN_3_4,
    PLAN_3_5,
    WORLD_3_FILLERS,
)
from game.sim.assemble_level import WorldTables, assemble_level

__pragma__("skip")
from typing import Any  # noqa: E402

# A wave plan or a beat is a config record (`game/config/record.py`), typed as Any there.
__pragma__("skip")
WavePlan = Any
__pragma__("noskip")

__pragma__("noskip")


TABLES = WorldTables(WORLD_3_DIFFICULTY, WORLD_3_FILLERS, WORLD_3_BOSSES)


def _level(id: str, scenery: Any, plan: WavePlan) -> GameLevel:
    return assemble_level(id, scenery, compose_beats(plan), TABLES)


# World 3 (P09; reworked at the reviewer's request, 2026-10-27): five levels of about 5 minutes,
# from the factories World 2 ended on to garden villages of small houses, each with a mini boss and
# a final boss.
WORLD_3 = [
    _level("3-1", LEVEL_3_1, PLAN_3_1),
    _level("3-2", LEVEL_3_2, PLAN_3_2),
    _level("3-3", LEVEL_3_3, PLAN_3_3),
    _level("3-4", LEVEL_3_4, PLAN_3_4),
    _level("3-5", LEVEL_3_5, PLAN_3_5),
]
