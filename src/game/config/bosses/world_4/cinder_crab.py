# Copyright (c) 2026 Renaud Guillon
"""4-1: the Cinder Crab, the Black sands' mini boss (specs/bosses/mini/4-1-cinder-crab.md).

Offsets in px from the boss's centre, X right and Y up (its claws reach down the screen, at -Y).
Each claw hangs on an arm that swings from its shoulder (D-061), and its outer finger opens and
closes on its own joint at the wrist, on the arm. The claws fire aimed spreads from their palms and
shield the core; the back mortar lobs slow, big bullets; the core's ring dome fires something new at
every stage (D-055).
"""

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


ORANGE = bullet("orange", 205)
RED = bullet("red", 200)
PURPLE = bullet("purple", 195)
MAGENTA = bullet("magenta", 210)
# The mortar's shells: slow, big balls of slag the player sidesteps (MB-CINDER-CRAB-10).
SLAG = bullet("orange", 120, 7)

# Where a left claw (at -X) is: its arm's shoulder on the carapace, its wrist (the finger's hinge),
# the claw's middle (the part's centre). The right claw mirrors them.
CRAB_ARM = record({"shoulder": [-16, -14], "wrist": [-24, -40], "claw": [-24, -36]})

# How the arms and fingers swing (D-061, MB-CINDER-CRAB-06): an arm `armDeg` either way every
# `armPeriod` seconds, the two out of step; a finger, drawn half open, `fingerDeg` either way (shut
# to wide open) every `fingerPeriod` seconds, snapping faster than the arms.
CRAB_SWING = record({"armDeg": 9, "armPeriod": 4.2, "fingerDeg": 13, "fingerPeriod": 1.5})


def claw(side: str) -> Any:
    """Return the claw on `side`: its arm on the shoulder and its finger on the wrist (D-061)."""
    s = 1 if side == "left" else -1
    joints: dict[str, Any] = {}
    joints["arm-" + side] = {
        "x": s * CRAB_ARM.shoulder[0],
        "y": CRAB_ARM.shoulder[1],
        # Out of step: the right arm a half swing behind the left one.
        "swing": {
            "amplitudeDeg": s * CRAB_SWING.armDeg,
            "period": CRAB_SWING.armPeriod,
            "phase": 0.2 if s > 0 else 0.7,
        },
    }
    # The finger opens outwards (the left one clockwise on screen).
    joints["finger-" + side] = {
        "x": s * CRAB_ARM.wrist[0],
        "y": CRAB_ARM.wrist[1],
        "parent": "arm-" + side,
        "swing": {
            "amplitudeDeg": s * CRAB_SWING.fingerDeg,
            "period": CRAB_SWING.fingerPeriod,
            "phase": 0 if s > 0 else 0.5,
        },
    }
    return joints


# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), at rest.

# The left claw's palm gun, between its fingers (mirrored on the right).
CRAB_PALM_GUN = [[-24, -52, 4.5]]
# The back mortar's mouth: its barrel leans forward over the carapace.
CRAB_MORTAR = [[0, 15, 17]]
# The ring dome's emitter on the carapace (the core's rings).
CRAB_DOME = [[0, -2, 15.5]]

# Where the mortar stands: on the back of the carapace, behind the dome.
CRAB_MORTAR_AT = [0, 24]

# 4-1: a wide, low crab-ship of soot-black armour, orange neon and molten seams, with two claws
# that open and close (MB-CINDER-CRAB-01). The claws fire aimed spreads and shield the core; the
# back mortar lobs slow, big slag; the core's dome fires rings, a spiral once alone. The ground
# slows (x0.5).
_CINDER_CRAB = record({
    "id": "cinder-crab",
    # Its core and parts, their health, and its points (MB-CINDER-CRAB-08, MB-CINDER-CRAB-15).
    "stats": stats(
        record({
            "id": "cinder-crab",
            "name": "Cinder Crab",
            "size": 3,
            "coreRadius": 13,
            "coreHealth": 2300,
            "points": 8000,
            "groundSpeed": 0.5,
            "parts": [
                part(
                    "claw-left",
                    [CRAB_ARM.claw[0], CRAB_ARM.claw[1]],
                    10,
                    500,
                    {"joint": "arm-left"},
                ),
                part(
                    "claw-right",
                    [-CRAB_ARM.claw[0], CRAB_ARM.claw[1]],
                    10,
                    500,
                    {"joint": "arm-right"},
                ),
                part("mortar", list(CRAB_MORTAR_AT), 12, 350, {"shields": False}),
            ],
            "joints": merge(claw("left"), claw("right")),
        })
    ),
    # Where it stops and how it moves in place (MB-CINDER-CRAB-07).
    "stopFraction": 0.72,
    "sway": {"amplitude": 65, "period": 7.5},
    "bob": {"amplitude": 7, "period": 3.6},
    "guns": {
        "core": {"ring": CRAB_DOME},
        "claw-left": {"gun": CRAB_PALM_GUN},
        "claw-right": {"gun": mirror(CRAB_PALM_GUN)},
        "mortar": {"gun": CRAB_MORTAR},
    },
    # The claws' spreads in every stage (MB-CINDER-CRAB-09), then the core's rings per stage
    # (MB-CINDER-CRAB-11).
    "stages": stages(
        [
            volley.aimed("claw-left", 2.6, 3, 13, RED, 0.8),
            volley.aimed("claw-right", 2.6, 3, 13, RED, 2.1),
            volley.aimed("mortar", 3.2, 1, 0, SLAG, 1.6),
        ],
        [
            [volley.ring("core", 3, 10, 18, ORANGE, 1.3)],
            [volley.ring("core", 2.4, 12, 15, ORANGE, 0.9)],
            [
                volley.ring("core", 2.4, 10, 0, PURPLE, 0.7),
                volley.ring("core", 2.4, 10, 18, ORANGE, 1.9),
            ],
            # Alone: a dense, slow-turning ring, and a three-armed spiral turning the other way.
            [
                volley.ring("core", 2.2, 16, 6, MAGENTA, 0.6),
                volley.ring("core", 0.4, 3, -27, RED, 0.3),
            ],
        ],
    ),
})

# Its hidden weapons (boss transformations, D-224, MB-CINDER-CRAB-13): at transformation 1 its
# flank armour bursts off, baring a dark metal frame, and a pair of gatling turrets unfold
# (MB-CINDER-CRAB-14).
CINDER_CRAB = with_weapons(
    _CINDER_CRAB,
    [
        hidden_weapon("gatling-left", "gatling", [-28, 21], 8, 400, 1, "red", 1.2, 11.7),
        hidden_weapon("gatling-right", "gatling", [28, 21], 8, 400, 1, "red", 2.0, 11.7),
    ],
    [
        # MB-CINDER-CRAB-13: the flank plating, a wedge of shell either side of the carapace from
        # the edge of its flat top (0.6 of its half width) out to its chine, station by station
        # (its nose at -Y; see `cinder_crab_model.CARAPACE`); the gatlings lie under it.
        armour_region(
            "flanks",
            1,
            [
                [7.2, -24],
                [15.6, -20],
                [24, -14],
                [28.8, -2],
                [27, 12],
                [19.2, 25],
                [8.4, 32],
                [14, 32],
                [32, 25],
                [45, 12],
                [48, -2],
                [40, -14],
                [26, -20],
                [12, -24],
            ],
            "wing",
        ),
    ],
)
