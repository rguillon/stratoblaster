# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-10 mini boss, the Monolith Array (specs/bosses/lab/L-10-monolith-array.md).

Three tall, dark obelisks hovering in a row over a low stone and metal platform: the big central
one is the core, the two side ones its parts. Lab boss: in the dev viewer only (no level brings it
in). Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

from game.config.bosses.boss_guns import gun_mount, laser_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import record

# MB-MONOLITH-ARRAY-01: the platform the obelisks hover over, its outline (right half, from the
# nose round to the back; mirrored) and its top's height.
PLATFORM_TOP = 5
PLATFORM_HALF = [
    [0, -21],
    [26, -18],
    [48, -8],
    [54, 4],
    [50, 16],
    [34, 19],
    [0, 17],
]
# An obelisk (MB-MONOLITH-ARRAY-02): its centre, its foot's half width (X) and half depth (Y), its
# top's, the height its foot hovers at (over its glowing pylon) and the height of its flat cap.
CORE_AT = [0, 4]
CORE_FOOT = [10, 7.5]
CORE_HEAD = [5.8, 4.3]
CORE_HOVER = 13
CORE_TOP = 52
SIDE_X = 41
SIDE_AT = [SIDE_X, 6]
SIDE_FOOT = [7, 5.6]
SIDE_HEAD = [4, 3.2]
SIDE_HOVER = 11
SIDE_TOP = 40
# The side monoliths' laser emitters, set in their front faces (MB-MONOLITH-ARRAY-03): their pivot
# and height.
EMITTER_Y = 2
EMITTER_HEIGHT = 22
# The core's sight turret on a plinth before the central obelisk, on the platform.
SIGHT_AT = [0, -14]
SIGHT_HEIGHT = 9.5

PURPLE = bullet("purple", 150)
RED = bullet("red", 215)

# The side monoliths' laser emitters: long lenses firing straight down the screen.
SIDE_LASER = {"size": 4, "bore": 2.2, "length": 9}
# The capstone rotor on the central obelisk: sixteen barrels, its slow, dense rings.
CROWN_ROTOR = {"size": 5.5, "barrels": 16, "layout": "ring", "bore": 0.75, "length": 4}
# The sight: one long barrel on a turret, its precise aimed shots.
SIGHT_GUN = {"size": 3.6, "barrels": 1, "bore": 1.1, "length": 9}

# MB-MONOLITH-ARRAY-07: two parts, the side monoliths, both shielding the core.
_MONOLITH_ARRAY = record({
    "id": "monolith-array",
    # Its points and its parts' drops (MB-MONOLITH-ARRAY-11).
    "stats": stats({
        "id": "monolith-array",
        "name": "Monolith Array",
        "size": 3.4,
        "coreRadius": 16,
        "coreHealth": 2100,
        "points": 5500,
        "groundSpeed": 0.5,
        "parts": [
            part("monolith-left", [-SIDE_X, SIDE_AT[1]], 13, 1150),
            part("monolith-right", [SIDE_X, SIDE_AT[1]], 13, 1150),
        ],
    }),
    # Where it stops and how it moves in place (MB-MONOLITH-ARRAY-06): slow and ominous.
    "stopFraction": 0.74,
    "sway": {"amplitude": 34, "period": 11},
    "bob": {"amplitude": 4, "period": 6},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-MONOLITH-ARRAY-03): a laser emitter in each side monolith's front
    # face, and the core's: the sixteen-barrelled rotor on the central obelisk's cap (its rings)
    # and the sight turret on the plinth before it (its aimed shots and bursts).
    "mounts": [
        laser_mount(
            "monolith-left", "monolith-left", [-SIDE_X, EMITTER_Y], EMITTER_HEIGHT, SIDE_LASER
        ),
        laser_mount(
            "monolith-right", "monolith-right", [SIDE_X, EMITTER_Y], EMITTER_HEIGHT, SIDE_LASER
        ),
        gun_mount("crown", "core", CORE_AT, CORE_TOP, CROWN_ROTOR),
        gun_mount("sight", "core", SIGHT_AT, SIGHT_HEIGHT, SIGHT_GUN),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-MONOLITH-ARRAY-08): the side
    # monoliths' long lasers in turn; the crown's rare, dense rings of 16 (one bullet a barrel), a
    # new turn and pace at every stage, and the sight's precise aimed shots and bursts.
    "stages": stages(
        [
            volley.laser("monolith-left", 7, 2.2, 2),
            volley.laser("monolith-right", 7, 2.2, 5.5),
        ],
        [
            [
                volley.ring("core", 3.4, 16, 11.25, PURPLE, 1.2),
                volley.aimed("core", 2.4, 1, 0, RED, 2),
            ],
            [
                volley.ring("core", 2.9, 16, -7, PURPLE, 0.8),
                volley.burst("core", 2.6, 3, 0.22, RED, 1.4),
            ],
            [
                volley.ring("core", 1.9, 16, 5.625, PURPLE, 0.6),
                volley.burst("core", 2.2, 4, 0.2, RED, 1),
            ],
        ],
    ),
})

# Where the lances stand: on the platform's front, either side of the sight's plinth.
LANCE_AT = [22, -9]
# The plinth plates over them (MB-MONOLITH-ARRAY-05): the right one's outline (mirrored) and their
# heights over the platform.
PLINTH_OUTLINE = [[13, -16], [32, -14], [33, -2], [13, -2]]
PLINTH_HEIGHTS = [PLATFORM_TOP - 0.5, PLATFORM_TOP + 4]

# Its transformation (MB-MONOLITH-ARRAY-10): once one side monolith is down, the plinth plates on
# the platform's front burst off, baring a dark metal frame, and a pair of lances unfold, pointing
# down the screen.
MONOLITH_ARRAY = with_weapons(
    _MONOLITH_ARRAY,
    [
        hidden_weapon(
            "lance-left",
            "lance",
            [-LANCE_AT[0], LANCE_AT[1]],
            8,
            920,
            1,
            "purple",
            1.2,
            [PLATFORM_TOP, PLATFORM_TOP + 4],
        ),
        hidden_weapon(
            "lance-right",
            "lance",
            LANCE_AT,
            8,
            920,
            1,
            "purple",
            2.4,
            [PLATFORM_TOP, PLATFORM_TOP + 4],
        ),
    ],
    [armour_region("plinths", 1, PLINTH_OUTLINE, "shell", PLINTH_HEIGHTS)],
)
