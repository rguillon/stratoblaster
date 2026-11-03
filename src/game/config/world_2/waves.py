# Copyright (c) 2026 Renaud Guillon
"""The wave scripts of World 2 (WLD-2-17, WLD-2-19), composed from its tier's kinds (ENM-49).

See `game/config/wave_plans.py`: each level cycles through the phrases of the kinds World 2 uses
(its tier's five), a beat every `gap` seconds shrinking over the level, its groups growing; the
filler fills the lulls (D-051).
"""

from game.config.wave_plans import PHRASE_LENGTH, compose_beats, level_plan, world_fillers

__all__ = [
    "PHRASE_LENGTH",
    "PLAN_2_1",
    "PLAN_2_2",
    "PLAN_2_3",
    "PLAN_2_4",
    "PLAN_2_5",
    "WORLD_2_FILLERS",
    "compose_beats",
]

PLAN_2_1 = level_plan(2, 1)
PLAN_2_2 = level_plan(2, 2)
PLAN_2_3 = level_plan(2, 3)
PLAN_2_4 = level_plan(2, 4)
PLAN_2_5 = level_plan(2, 5)

# The filler of each level (LVL-2-1-09 … LVL-2-5-09), from the level's divers and shooters; each
# level is fuller per minute than the one before (WLD-2-20).
WORLD_2_FILLERS = world_fillers(2)
