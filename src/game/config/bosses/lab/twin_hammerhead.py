# Copyright (c) 2026 Renaud Guillon
"""The Twin Hammerhead (the Lab's L-2 mini boss, specs/bosses/lab/L-2-twin-hammerhead.md).

A catamaran of two hammerhead-shark hulls side by side, wide apart, joined by a bony bridge with
the core on it. Offsets in px from the boss's centre, X right and Y up (its nose points down, at
-Y). Its two hammer cannons sweep aimed spreads at the player from both flanks, so their streams
cross over the player (MB-TWIN-HAMMERHEAD-08); the missile block on the bridge launches homing
missiles. Lab boss: in the dev viewer only, no level brings it in.
"""

import math

from game.config.bosses.boss_guns import gun_mount, missile_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import record

RED = bullet("red", 190)
ORANGE = bullet("orange", 180)

# Where each hull runs (the right one at +X, the left one its mirror image): its centre line's X,
# and the Y of the middle of its hammer head (MB-TWIN-HAMMERHEAD-01).
HULL_X = 36
HAMMER_Y = -30
# Heights of the bridge's deck (the core's, under its armour) and of the hammer heads' top.
BRIDGE_TOP = 5
HAMMER_TOP = 7.2

# The hammer cannons' turrets: three barrels side by side, sweeping their aimed spreads
# (MB-TWIN-HAMMERHEAD-03).
HAMMER_CANNON = {"size": 6.5, "barrels": 3, "gap": 3.2, "bore": 1.2, "length": 9}

_TWIN_HAMMERHEAD = record({
    "id": "twin-hammerhead",
    # Its points and its parts' drops (MB-TWIN-HAMMERHEAD-11).
    "stats": stats({
        "id": "twin-hammerhead",
        "name": "Twin Hammerhead",
        "size": 3.2,
        "coreRadius": 18,
        "coreHealth": 1050,
        "points": 3500,
        "groundSpeed": 0.7,
        "parts": [
            part("cannon-left", [-HULL_X, HAMMER_Y], 13, 600),
            part("cannon-right", [HULL_X, HAMMER_Y], 13, 600),
            part("missile-block", [0, 19], 11, 680),
        ],
    }),
    # Where it stops and how it moves in place (MB-TWIN-HAMMERHEAD-06).
    "stopFraction": 0.72,
    "sway": {"amplitude": 65, "period": 7},
    "bob": {"amplitude": 8, "period": 3.5},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-TWIN-HAMMERHEAD-03): a cannon turret on each hammer head, a block
    # of four missile ports on the bridge's rear hump, and the core's on the bridge: the fan turret
    # on its front lip (its fans, aimed spreads and bursts) and the rotor on the core's dome (its
    # last ring), under a hatch until then.
    "mounts": [
        gun_mount("cannon-left", "cannon-left", [-HULL_X, HAMMER_Y], HAMMER_TOP, HAMMER_CANNON),
        gun_mount("cannon-right", "cannon-right", [HULL_X, HAMMER_Y], HAMMER_TOP, HAMMER_CANNON),
        missile_mount("missile-block", "missile-block", [0, 19], 9.5, 4),
        gun_mount(
            "bridge-gun",
            "core",
            [0, -13],
            BRIDGE_TOP + 0.6,
            {"size": 5.5, "barrels": 3, "gap": 2.9, "bore": 1.1, "length": 7},
        ),
        gun_mount(
            "bridge-rotor",
            "core",
            [0, 4],
            12.4,
            {"size": 4.6, "barrels": 12, "layout": "ring", "bore": 0.8, "length": 3.4},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-TWIN-HAMMERHEAD-08). The two hammer
    # cannons fire their aimed spreads a beat apart, from 72 px apart: the streams cross over the
    # player. BOSS-58: the bridge turret's fans are 12° apart, as the World 1 turrets'.
    "stages": stages(
        [
            volley.aimed("cannon-left", 2.4, 3, 10, RED, 1),
            volley.aimed("cannon-right", 2.4, 3, 10, RED, 1.3),
            volley.missiles("missile-block", 5.5, 2, 30, 3),
        ],
        [
            [volley.fan("core", 3, 3, 12, ORANGE, 1.6)],
            [volley.aimed("core", 2.6, 3, 12, ORANGE, 0.8)],
            [volley.burst("core", 2.2, 4, 0.15, ORANGE, 0.6)],
            [volley.ring("core", 1.6, 12, 9, ORANGE, 0.4)],
        ],
    ),
})

# The bridge's armour plates (MB-TWIN-HAMMERHEAD-05): the right one (x 7 to 25), its mirror image
# the left one; the core's dome and its hatch stand between them.
BRIDGE_PLATE = [[7, -7], [25, -7], [25, 14], [7, 14]]

# Its transformation (D-224, MB-TWIN-HAMMERHEAD-10): once two of its parts are gone the bridge's
# armour plates burst off, baring a dark metal frame, and a pair of gatlings unfold on the bridge.
TWIN_HAMMERHEAD = with_weapons(
    _TWIN_HAMMERHEAD,
    [
        hidden_weapon("gatling-left", "gatling", [-16, 4], 8, 540, 1, "orange", 1.2, 9.5),
        hidden_weapon("gatling-right", "gatling", [16, 4], 8, 540, 1, "orange", 2.0, 9.5),
    ],
    [
        armour_region("bridge", 1, BRIDGE_PLATE, "wing"),
        # The hatch over the bridge rotor (BOSS-58): it bursts as the rotor comes into use, in its
        # last stage, and the rotor rises out of it.
        armour_region(
            "rotor-hatch",
            None,
            [[6 * math.cos(k * math.pi / 4), 4 + 6 * math.sin(k * math.pi / 4)] for k in range(8)],
            "ring",
            None,
            False,
            "bridge-rotor",
        ),
    ],
)
