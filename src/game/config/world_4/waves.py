# Copyright (c) 2026 Renaud Guillon
"""The wave scripts of World 4 (WLD-4-17, WLD-4-19), composed from its tier's kinds (ENM-49).

See `game/config/wave_plans.py`: each level cycles through the phrases of the kinds World 4 uses
(its tier's five), a beat every `gap` seconds shrinking over the level, its groups growing; the
filler fills the lulls (D-051).
"""

from game.config.wave_plans import PHRASE_LENGTH, compose_beats, level_plan, world_fillers

__all__ = [
    "PHRASE_LENGTH",
    "PLAN_4_1",
    "PLAN_4_2",
    "PLAN_4_3",
    "PLAN_4_4",
    "PLAN_4_5",
    "WORLD_4_FILLERS",
    "compose_beats",
]

PLAN_4_1 = level_plan(4, 1)
PLAN_4_2 = level_plan(4, 2)
PLAN_4_3 = level_plan(4, 3)
PLAN_4_4 = level_plan(4, 4)
PLAN_4_5 = level_plan(4, 5)

# The filler of each level (LVL-4-1-09 … LVL-4-5-09), from the level's divers and shooters; each
# level is fuller per minute than the one before (WLD-4-20).
WORLD_4_FILLERS = world_fillers(4)
