"""World 2, ported from `game/sim/world-2.ts`."""

from org.transcrypt.stubs.browser import __pragma__

from core.content.game_level import GameLevel
from game.config.world_2.bosses import WORLD_2_BOSSES
from game.config.world_2.difficulty import WORLD_2_DIFFICULTY
from game.config.world_2.scenery import LEVEL_2_1, LEVEL_2_2, LEVEL_2_3, LEVEL_2_4, LEVEL_2_5
from game.config.world_2.waves import (
    PLAN_2_1,
    PLAN_2_2,
    PLAN_2_3,
    PLAN_2_4,
    PLAN_2_5,
    WORLD_2_FILLERS,
    compose_beats,
)
from game.sim.assemble_level import WorldTables, assemble_level

__pragma__("skip")
from typing import Any  # noqa: E402

from core.scenery.scenery_level import SceneryLevel  # noqa: E402

# A wave plan or a beat is a config record (`game/config/record.py`), typed as Any there.
__pragma__("skip")
WavePlan = Any
__pragma__("noskip")

__pragma__("noskip")


TABLES = WorldTables(WORLD_2_DIFFICULTY, WORLD_2_FILLERS, WORLD_2_BOSSES)


def _level(id: str, scenery: SceneryLevel, plan: WavePlan) -> GameLevel:
    return assemble_level(id, scenery, compose_beats(plan), TABLES)


# World 2, the Industrial Desert (P08, reworked at the reviewer's request, 2026-10-27): five
# levels of about 5 minutes, from the deep desert to dense factories, each with a mini boss and a
# final boss.
WORLD_2 = [
    _level("2-1", LEVEL_2_1, PLAN_2_1),
    _level("2-2", LEVEL_2_2, PLAN_2_2),
    _level("2-3", LEVEL_2_3, PLAN_2_3),
    _level("2-4", LEVEL_2_4, PLAN_2_4),
    _level("2-5", LEVEL_2_5, PLAN_2_5),
]
