"""P09-R09, 3-1: the Mangrove Croc, the River delta's mini boss (ported from
`config/bosses/world-3/mangrove-croc.ts`).

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). Its two jaws
open and close on their hinges (D-061) around the jaw cannon, opening wide as it fires; the two
side pontoons fire fans and shield the core, whose ring dome fires something new at every stage
(D-055).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.record import record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

GREEN = bullet("green", 205)
ORANGE = bullet("orange", 195)
BLUE = bullet("blue", 192)
PURPLE = bullet("purple", 200)

# The jaws: where the left one (at -X) is hinged and how long it is (mirrored on the right).
CROC_JAW = record({"hinge": [-7, -27], "tip": [-5, -53]})

# How the jaws swing (D-061): drawn half open, they swing `amplitudeDeg` either way, from shut to
# wide open, once every `period` seconds, the jaw cannon's burst coming when they are wide open.
# The entry of the boss takes `entrySeconds` (from its spawn above the top edge to its place, as
# `BOSS_TIMING` brings it in), so the jaws' phase puts the first wide-open moment on the first
# burst; later stages restart their volleys at a stage change, so the two drift apart after the
# first part is destroyed.
CROC_JAW_SWING = record({"amplitudeDeg": 9, "period": 2.4, "entrySeconds": 4.28})

# The jaw cannon's burst: every jaw swing, first at this time of the fight; 3 shots.
BURST = record({"first": 1.2, "gap": 0.14, "count": 3})

# Turns from the boss's arrival to the middle of the first burst, when the jaws are widest.
JAW_PHASE = (
    0.25
    - (CROC_JAW_SWING.entrySeconds + BURST.first + ((BURST.count - 1) * BURST.gap) / 2)
    / CROC_JAW_SWING.period
)


def jaw(side: str) -> Any:
    """The jaw on `side` (D-061): it opens outwards (the left one clockwise on screen)."""
    s = 1 if side == "left" else -1
    amplitude_deg = CROC_JAW_SWING.amplitudeDeg
    period = CROC_JAW_SWING.period
    return {
        "x": s * CROC_JAW.hinge[0],
        "y": CROC_JAW.hinge[1],
        "swing": {
            "amplitudeDeg": s * amplitude_deg,
            "period": period,
            "phase": JAW_PHASE - math.floor(JAW_PHASE),
        },
    }


# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The jaw cannon's barrel, in the croc's throat between the jaws.
CROC_JAW_CANNON = [[0, -47, 4.5]]
# The right pontoon's twin fan guns, at its bow (mirrored on the left).
CROC_PONTOON_GUNS = twin(27, -14, 4.2, 2.6)
# The ring dome's emitter on the croc's back (the core's rings).
CROC_DOME = [[0, 12, 15.5]]

# Where the parts sit: the jaw cannon in the throat, the pontoons either side.
CROC_PARTS = record({"jaw": [0, -37], "pontoon": [27, 4]})

# 3-1: a long, low hover-gunboat with jaws that open and close and green neon eyes (P09-R09).
# The jaw cannon fires aimed bursts as the jaws open; the side pontoons fire fans and shield the
# core; the core's ring dome fires rings, a spiral once alone. The fight is a chase up the delta
# (ground x1.4).
MANGROVE_CROC = record(
    {
        "id": "mangrove-croc",
        # Angry after each destroyed part (D-063), heat 4.5 (P09-R10).
        "rage": rage.vortex(4.5, "green", "orange"),
        "stats": stats(
            record(
                {
                    "id": "mangrove-croc",
                    "name": "Mangrove Croc",
                    "size": 3,
                    "coreRadius": 15,
                    "coreHealth": 1450,
                    "points": 7500,
                    "groundSpeed": 1.4,
                    "parts": [
                        part(
                            "pontoon-left",
                            [-CROC_PARTS.pontoon[0], CROC_PARTS.pontoon[1]],
                            12,
                            625,
                        ),
                        part("pontoon-right", list(CROC_PARTS.pontoon), 12, 625),
                        part("jaw-cannon", list(CROC_PARTS.jaw), 10, 500, {"shields": False}),
                    ],
                    "joints": {"jaw-left": jaw("left"), "jaw-right": jaw("right")},
                }
            )
        ),
        "stopFraction": 0.72,
        "sway": {"amplitude": 70, "period": 7},
        "bob": {"amplitude": 8, "period": 3.4},
        "guns": {
            "core": {"ring": CROC_DOME},
            "jaw-cannon": {"gun": CROC_JAW_CANNON},
            "pontoon-left": {"gun": mirror(CROC_PONTOON_GUNS)},
            "pontoon-right": {"gun": CROC_PONTOON_GUNS},
        },
        "stages": stages(
            [
                volley.burst(
                    "jaw-cannon", CROC_JAW_SWING.period, BURST.count, BURST.gap, GREEN, BURST.first
                ),
                volley.fan("pontoon-left", 2.8, 3, 14, ORANGE, 0.7, -12),
                volley.fan("pontoon-right", 2.8, 3, 14, ORANGE, 2.1, 12),
            ],
            [
                [volley.ring("core", 3, 10, 18, BLUE, 1.6)],
                [volley.ring("core", 2.5, 12, 15, BLUE, 1)],
                [
                    volley.ring("core", 2.4, 10, 0, BLUE, 0.8),
                    volley.ring("core", 2.4, 10, 18, PURPLE, 2),
                ],
                # Alone: a spiral, and a slow-turning ring under it.
                [
                    volley.ring("core", 0.42, 4, 23, GREEN, 0.4),
                    volley.ring("core", 2.6, 14, 7, PURPLE, 1),
                ],
            ],
        ),
    }
)
