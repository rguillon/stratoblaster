# Copyright (c) 2026 Renaud Guillon
"""The wave scripts of World 3 (WLD-3-17, WLD-3-19), composed from its tier's kinds (ENM-49).

See `game/config/wave_plans.py`: each level cycles through the phrases of the kinds World 3 uses
(its tier's five), a beat every `gap` seconds shrinking over the level, its groups growing; the
filler fills the lulls (D-051).
"""

from game.config.wave_plans import PHRASE_LENGTH, compose_beats, level_plan, world_fillers

__all__ = [
    "PHRASE_LENGTH",
    "PLAN_3_1",
    "PLAN_3_2",
    "PLAN_3_3",
    "PLAN_3_4",
    "PLAN_3_5",
    "WORLD_3_FILLERS",
    "compose_beats",
]

PLAN_3_1 = level_plan(3, 1)
PLAN_3_2 = level_plan(3, 2)
PLAN_3_3 = level_plan(3, 3)
PLAN_3_4 = level_plan(3, 4)
PLAN_3_5 = level_plan(3, 5)

# The filler of each level (LVL-3-1-09 … LVL-3-5-09), from the level's divers and shooters; each
# level is fuller per minute than the one before (WLD-3-20).
WORLD_3_FILLERS = world_fillers(3)
