# Copyright (c) 2026 Renaud Guillon
"""World 4."""

from core.content.game_level import GameLevel
from game.config.world_4.bosses import WORLD_4_BOSSES
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

# isort: split
# __pragma__ ("skip")
from typing import Any

# A wave plan or a beat is a config record (`game/config/record.py`), typed as Any there.
WavePlan = Any
# __pragma__ ("noskip")


TABLES = WorldTables(WORLD_4_FILLERS, WORLD_4_BOSSES)
# Each level's scenery, by level id (to compose a level again with other enemies, D-307).
SCENERIES = {
    "4-1": LEVEL_4_1,
    "4-2": LEVEL_4_2,
    "4-3": LEVEL_4_3,
    "4-4": LEVEL_4_4,
    "4-5": LEVEL_4_5,
}


def _level(level_id: str, scenery: Any, plan: WavePlan) -> GameLevel:
    # Its waves composed from its plan (WLD-4-18).
    return assemble_level(level_id, scenery, plan, TABLES)


# World 4 (WLD-4-01; reworked at the reviewer's request, 2026-10-27): five levels of about 5
# minutes, from the garden villages World 3 ended on to a downtown of skyscrapers, each with a mini
# boss and a final boss.
WORLD_4 = [
    _level("4-1", LEVEL_4_1, PLAN_4_1),  # LVL-4-1-04
    _level("4-2", LEVEL_4_2, PLAN_4_2),  # LVL-4-2-04
    _level("4-3", LEVEL_4_3, PLAN_4_3),  # LVL-4-3-04
    _level("4-4", LEVEL_4_4, PLAN_4_4),  # LVL-4-4-04
    _level("4-5", LEVEL_4_5, PLAN_4_5),  # LVL-4-5-04
]
