# Copyright (c) 2026 Renaud Guillon
"""The Kite Bulwark, the Lab's L-15 mini boss (specs/bosses/lab/L-15-kite-bulwark.md).

Lab boss: in the dev viewer only, no level brings it in. A huge box-kite glider fortress: two very
wide braced wings of fabric stretched on metal spars, each with its box-kite cells, either side of
a central armoured nacelle, tow cables trailing behind it. It fires wide, slow fans from its
wingtip gun pods and lobs flak from its tail winch. Once both wingtip pods are gone its wings fold
back about their trailing roots into a narrow dart (it changes shape, BOSS-45), and a sweeper
laser rides in on each folded wing: from wide, slow fans to fast, diving lasers.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, bursting, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import move_point, moving_region, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


GREEN = bullet("green", 140)
ORANGE = bullet("orange", 185)
RED = bullet("red", 200)
# Its winch's flak (MB-KITE-BULWARK-08): a big, slow shell bursting into a ring of 8.
FLAK = bursting("orange", 95, 7, [1.3, 8, bullet("red", 150)])

# MB-KITE-BULWARK-01: the nacelle, from its nose to its tail, its half width and its deck's top.
NOSE = -36
TAIL = 30
NACELLE_HALF = 10
NACELLE_TOP = 13

# MB-KITE-BULWARK-05: the right wing as drawn, spread wide open (at rest): from its leading root
# out to its tip and back to its trailing root. Its spars, ribs and fabric are drawn from it.
WING = [[9, -12], [40, -8], [62, -4], [64, 3], [62, 10], [40, 11], [9, 12]]
# Its trailing root (the hinge `[x, y, height]` it folds back about) and how far back it folds
# (degrees about the vertical, counter-clockwise seen from above: its tip goes back).
WING_PIVOT = [9.0, 12.0, 6.0]
FOLD = 72
WING_SWING = swing(WING_PIVOT, "up", [0, FOLD])
# The heights the wing is drawn between: its spars' foot and the fabric's top.
WING_Y = [6, 9.5]


def _tenth(value: float) -> float:
    """`value` rounded to a tenth."""
    return math.floor(value * 10 + 0.5) / 10


def folded(spot: list[Any]) -> list[float]:
    """Where `spot` of the right wing as drawn lies once the wing has folded back."""
    q = move_point(WING_SWING, FOLD, [spot[0], spot[1], 0])
    return [_tenth(q[0]), _tenth(q[1])]


# The wingtip gun pods (MB-KITE-BULWARK-03): on the wing, inside its outer box-kite cell.
POD_AT = [52, 3]
POD_TOP = 13
POD_GUN = {"size": 4.6, "barrels": 3, "gap": 1.3, "bore": 1.1, "length": 7}
# The tail winch's flak mortar: one fat barrel in a cradle on a turntable.
WINCH_AT = [0, 31]
WINCH_GUN_AT = [0, 33]
WINCH_TOP = 12
WINCH_MORTAR = {
    "size": 5.5,
    "barrels": 1,
    "bore": 3.2,
    "length": 4.5,
    "style": "mortar",
    "axis": 0.8,
}
# The core's guns: a twin-barrelled turret in the nacelle's chin, and the spine rotor (its last
# ring), under a hatch until then.
CHIN_AT = [0, -24]
CHIN_GUN = {"size": 4.4, "barrels": 2, "gap": 1.4, "bore": 1.1, "length": 7}
ROTOR_AT = [0, 2]
ROTOR = {"size": 4.4, "barrels": 10, "layout": "ring", "bore": 0.8, "length": 3.2}

_KITE_BULWARK = record({
    "id": "kite-bulwark",
    # Its points and its parts' drops (MB-KITE-BULWARK-11).
    "stats": stats({
        "id": "kite-bulwark",
        "name": "Kite Bulwark",
        "size": 3.8,
        "coreRadius": 14,
        "coreHealth": 1700,
        "points": 5000,
        "groundSpeed": 1.2,
        "parts": [
            part("pod-left", [-POD_AT[0], POD_AT[1]], 10, 700),
            part("pod-right", POD_AT, 10, 700),
            part("winch", WINCH_AT, 11, 800),
        ],
    }),
    # Where it stops and how it moves in place (MB-KITE-BULWARK-06): a wide kite riding the wind.
    "stopFraction": 0.72,
    "sway": {"amplitude": 50, "period": 7},
    "bob": {"amplitude": 7, "period": 3.2},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-KITE-BULWARK-03): a three-barrelled turret on each wingtip pod,
    # the flak mortar on the tail winch, and the core's: the chin turret and the spine rotor.
    "mounts": [
        gun_mount("pod-left", "pod-left", [-POD_AT[0], POD_AT[1]], POD_TOP, POD_GUN),
        gun_mount("pod-right", "pod-right", POD_AT, POD_TOP, POD_GUN),
        gun_mount("winch", "winch", WINCH_GUN_AT, WINCH_TOP, WINCH_MORTAR),
        gun_mount("chin", "core", CHIN_AT, NACELLE_TOP, CHIN_GUN),
        gun_mount("spine-rotor", "core", ROTOR_AT, NACELLE_TOP + 1, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-KITE-BULWARK-08): the pods' wide,
    # slow fans of 7 sweep down from each wingtip, crossing under it; the winch lobs flak at the
    # player. The core adds an aimed shot, an aimed spread, fast bursts once it has folded, then the
    # spine rotor's rings of 10.
    "stages": stages(
        [
            volley.fan("pod-left", 3.2, 7, 10, GREEN, 1, -10),
            volley.fan("pod-right", 3.2, 7, 10, GREEN, 2.6, 10),
            volley.aimed("winch", 2.8, 1, 0, FLAK, 1.8),
        ],
        [
            [volley.aimed("core", 3, 1, 0, ORANGE, 1.4)],
            [volley.aimed("core", 2.4, 3, 10, ORANGE, 0.8)],
            [volley.burst("core", 1.5, 5, 0.1, RED, 0.6)],
            [
                volley.ring("core", 1.5, 10, 9, ORANGE, 0.4),
                volley.burst("core", 2, 3, 0.1, RED, 1),
            ],
        ],
    ),
})

# Where the sweepers ride (MB-KITE-BULWARK-10): on each wing's inner cell, folded back.
SWEEPER_SPOT = [28, 1]
SWEEPER_AT = folded(SWEEPER_SPOT)
SWEEPER_POD = [WING_Y[1], WING_Y[1] + 3]

# Its transformation (BOSS-45, MB-KITE-BULWARK-10): once both wingtip pods are gone its wings fold
# back into a narrow dart, and a sweeper rides in on each. The spine hatch over its rotor bursts as
# the rotor comes into use, in its last stage (BOSS-58).
KITE_BULWARK = with_weapons(
    merge(_KITE_BULWARK, {"transformParts": [["pod-left", "pod-right"]]}),
    [
        hidden_weapon(
            "sweeper-left",
            "sweeper",
            [-SWEEPER_AT[0], SWEEPER_AT[1]],
            7,
            640,
            1,
            "red",
            1.2,
            SWEEPER_POD,
        ),
        hidden_weapon("sweeper-right", "sweeper", SWEEPER_AT, 7, 640, 1, "red", 2.0, SWEEPER_POD),
    ],
    concat(
        moving_region("wings", 1, WING, WING_SWING, None, [WING_Y[0], 1000]),
        [
            armour_region(
                "rotor-hatch",
                None,
                [
                    [
                        ROTOR_AT[0] + 6 * math.cos(k * math.pi / 4 + math.pi / 8),
                        ROTOR_AT[1] + 6 * math.sin(k * math.pi / 4 + math.pi / 8),
                    ]
                    for k in range(8)
                ],
                "ring",
                None,
                False,
                "spine-rotor",
            ),
        ],
    ),
)
