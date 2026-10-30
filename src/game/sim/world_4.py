"""World 4, ported from `game/sim/world-4.ts`."""

from org.transcrypt.stubs.browser import __pragma__

from core.content.game_level import GameLevel
from game.config.world_2.waves import compose_beats
from game.config.world_4.bosses import WORLD_4_BOSSES
from game.config.world_4.difficulty import WORLD_4_DIFFICULTY
from game.config.world_4.scenery import LEVEL_4_1, LEVEL_4_2, LEVEL_4_3, LEVEL_4_4, LEVEL_4_5
from game.config.world_4.waves import (
    PLAN_4_1,
    PLAN_4_2,
    PLAN_4_3,
    PLAN_4_4,
    PLAN_4_5,
    WORLD_4_FILLERS,
)
from game.sim.assemble_level import WorldTables, assemble_level

__pragma__("skip")
from typing import Any  # noqa: E402

# A wave plan or a beat is a config record (`game/config/record.py`), typed as Any there.
__pragma__("skip")
WavePlan = Any
__pragma__("noskip")

__pragma__("noskip")


TABLES = WorldTables(WORLD_4_DIFFICULTY, WORLD_4_FILLERS, WORLD_4_BOSSES)


def _level(id: str, scenery: Any, plan: WavePlan) -> GameLevel:
    return assemble_level(id, scenery, compose_beats(plan), TABLES)


# World 4 (P10; reworked at the reviewer's request, 2026-10-27): five levels of about 5 minutes,
# from the garden villages World 3 ended on to a downtown of skyscrapers, each with a mini boss
# and a final boss.
WORLD_4 = [
    _level("4-1", LEVEL_4_1, PLAN_4_1),
    _level("4-2", LEVEL_4_2, PLAN_4_2),
    _level("4-3", LEVEL_4_3, PLAN_4_3),
    _level("4-4", LEVEL_4_4, PLAN_4_4),
    _level("4-5", LEVEL_4_5, PLAN_4_5),
]
