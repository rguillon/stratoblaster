# Copyright (c) 2026 Renaud Guillon
"""The Rocket Interceptor, the Lab's L-20 mini boss (specs/bosses/lab/L-20-rocket-interceptor.md).

Lab boss: in the dev viewer only, no level brings it in. A gigantic rocket-plane strapped to
boosters, seen from above: a slim core plane with stubby delta wings riding between two big
strap-on booster rockets, held to its wingtips by pylons. Its boosters fire salvos of homing
missiles from the blocks on their backs, its tail turret lobs flak. Once both boosters are wrecked
they are jettisoned (they retire, BOSS-46, peeling away outward and falling behind), and the core
plane unfolds: its stub wings telescope out in two sections into the room the boosters left (a
moving piece, BOSS-45), and the doors at each new wingtip open on a lance: from missile and flak
salvos to precise lasers.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount, missile_mount
from game.config.bosses.boss_kit import bullet, bursting, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide
from game.config.record import concat, merge, record

ORANGE = bullet("orange", 185)
RED = bullet("red", 205)
# Its tail turret's flak (MB-ROCKET-INTERCEPTOR-08): a big, slow shell bursting into a ring of 8.
FLAK = bursting("orange", 100, 7, [1.2, 8, bullet("red", 155)])

# MB-ROCKET-INTERCEPTOR-01: the core plane's fuselage, nose to tail, and its spine's top.
NOSE = -52
TAIL = 36
SPINE_TOP = 12
# Its stub delta wing (the right one; mirrored): from its leading root out to its tip and back to
# its trailing root; the heights it is drawn between (bottom, edge's waist, top).
WING = [[7, -10], [22, 8], [22, 26], [7, 28]]  # type: list[list[float]]
WING_Y = [2.5, 5.2, 6.5]  # type: list[float]
# The boosters (MB-ROCKET-INTERCEPTOR-02): their axis' X and height, their radius, the tip of their
# nose cone, where their casing starts and ends (the nose cone is their part, the casing is the
# rig's), and their nozzles' exit. The saddle on their back the missile block stands on.
BOOSTER_X = 33
BOOSTER_AXIS = 10.5
BOOSTER_R = 9.5
BOOSTER_TIP = -48
BOOSTER_CASING = [-30, 30]  # type: list[float]
BOOSTER_EXIT = 39
BOOSTER_TOP = 20.5
# The wing extension (MB-ROCKET-INTERCEPTOR-05): its outer section as drawn once out (the right
# one; mirrored), between its heights; it rests `EXT_IN` px in, inside the stub wing, and slides
# out. The middle section (the rig's) slides half as far, from `MID_IN` px in.
EXTENSION = [
    [34, 10.5],
    [47, 10.5],
    [51, 14],
    [51, 20],
    [47, 23.5],
    [34, 23.5],
]  # type: list[list[float]]
EXT_Y = [2.8, 5.2]  # type: list[float]
EXT_IN = 29
MID_IN = 15
MID = [20, 36, 9.5, 24.5]  # type: list[float]

# The guns (BOSS-58, MB-ROCKET-INTERCEPTOR-03): a block of four missile ports on each booster's
# back saddle, the tail turret's flak mortar, and the core's: a twin chin gun under the nose and
# the spine rotor (its last ring), under a hatch until then.
MISSILE_AT = [BOOSTER_X, -14]
FLAK_AT = [0, 30]
FLAK_GUN_AT = [0, 31]
FLAK_TOP = 11.5
FLAK_MORTAR = {
    "size": 5.2,
    "barrels": 1,
    "bore": 3,
    "length": 4.4,
    "style": "mortar",
    "axis": 0.8,
}
CHIN_AT = [0, -40]
CHIN_TOP = 8
CHIN_GUN = {"size": 4.2, "barrels": 2, "gap": 1.3, "bore": 1, "length": 7}
ROTOR_AT = [0, 4]
ROTOR = {"size": 4.4, "barrels": 10, "layout": "ring", "bore": 0.8, "length": 3.2}

_ROCKET_INTERCEPTOR = record({
    "id": "rocket-interceptor",
    # Its points and its parts' drops (MB-ROCKET-INTERCEPTOR-11).
    "stats": stats({
        "id": "rocket-interceptor",
        "name": "Rocket Interceptor",
        "size": 3.6,
        "coreRadius": 13,
        "coreHealth": 1620,
        "points": 5200,
        "groundSpeed": 1.3,
        "parts": [
            # D-228: wrecked, they are jettisoned at its transformation (they call for it).
            part("booster-left", [-BOOSTER_X, -24], 13, 750, {"retire": 1}),
            part("booster-right", [BOOSTER_X, -24], 13, 750, {"retire": 1}),
            part("flak", FLAK_AT, 9, 800),
        ],
    }),
    # Where it stops and how it moves in place (MB-ROCKET-INTERCEPTOR-06): a fast interceptor,
    # wide quick sways.
    "stopFraction": 0.72,
    "sway": {"amplitude": 62, "period": 6.4},
    "bob": {"amplitude": 6, "period": 3},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-ROCKET-INTERCEPTOR-03).
    "mounts": [
        missile_mount(
            "booster-left",
            "booster-left",
            [-MISSILE_AT[0], MISSILE_AT[1]],
            BOOSTER_TOP + 3,
            4,
        ),
        missile_mount("booster-right", "booster-right", MISSILE_AT, BOOSTER_TOP + 3, 4),
        gun_mount("flak", "flak", FLAK_GUN_AT, FLAK_TOP, FLAK_MORTAR),
        gun_mount("chin", "core", CHIN_AT, CHIN_TOP, CHIN_GUN),
        gun_mount("spine-rotor", "core", ROTOR_AT, SPINE_TOP, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-ROCKET-INTERCEPTOR-08): the
    # boosters' homing pairs, one after the other, and the tail's flak at the player; the core's
    # aimed shot, an aimed spread, fast bursts once it has unfolded, then the spine rotor's rings.
    "stages": stages(
        [
            volley.missiles("booster-left", 5.5, 2, 24, 1.2),
            volley.missiles("booster-right", 5.5, 2, 24, 3.9),
            volley.aimed("flak", 3, 1, 0, FLAK, 2.2),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, ORANGE, 1.4)],
            [volley.aimed("core", 2.4, 3, 10, ORANGE, 0.8)],
            [volley.burst("core", 1.6, 5, 0.1, RED, 0.6)],
            [
                volley.ring("core", 1.5, 10, 9, ORANGE, 0.4),
                volley.burst("core", 2, 3, 0.1, RED, 1),
            ],
        ],
    ),
})

# Where the lances ride (MB-ROCKET-INTERCEPTOR-10): on each wing's outer section, slid out, under
# the doors of its tip.
LANCE_AT = [44, 17]
LANCE_POD = [EXT_Y[1], EXT_Y[1] + 3.5]

# Its transformation (BOSS-45, BOSS-46, MB-ROCKET-INTERCEPTOR-10): once both boosters are wrecked
# they are jettisoned, its wings telescope out and a lance rides out on each. The spine hatch over
# its rotor bursts as the rotor comes into use, in its last stage (BOSS-58).
ROCKET_INTERCEPTOR = with_weapons(
    merge(_ROCKET_INTERCEPTOR, {"transformParts": [["booster-left", "booster-right"]]}),
    [
        hidden_weapon(
            "lance-left", "lance", [-LANCE_AT[0], LANCE_AT[1]], 7, 640, 1, "red", 1.2, LANCE_POD
        ),
        hidden_weapon("lance-right", "lance", LANCE_AT, 7, 640, 1, "red", 3.6, LANCE_POD),
    ],
    concat(
        moving_region("wing-ext", 1, EXTENSION, slide([[-EXT_IN, 0, 0], [0, 0, 0]]), None, EXT_Y),
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
