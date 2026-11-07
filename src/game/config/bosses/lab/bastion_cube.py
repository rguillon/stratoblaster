# Copyright (c) 2026 Renaud Guillon
"""The Bastion Cube, the Lab's L-7 mini boss (specs/bosses/lab/L-7-bastion-cube.md).

Lab boss: in the dev viewer only, no level brings it in. A square, stepped block fortress seen from
above: a ziggurat of plated steel tiers on a cross-shaped plinth, a bastion block in each corner
with a tower on it, a gatehouse jutting out of its front. It fires in grids: straight walls of
bullets from the gatehouse, aimed bursts from the front towers. Once both front towers are gone its
four corner blocks slide out on their rails, opening the cube (it changes shape, BOSS-45), and a
gatling rides out on each rear tower.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide
from game.config.record import concat, merge, record

RED = bullet("red", 185)
ORANGE = bullet("orange", 175)
MAGENTA = bullet("magenta", 190)

# MB-BASTION-CUBE-01: the cube's half width (its plinth's outer walls), the plinth's height, and the
# inner edge of its corner notches (each corner block fills one, from `NOTCH` out to `HALF`).
HALF = 46
NOTCH = 25
PLINTH_TOP = 10
# Its steel tiers over the plinth: `[half width, top]` each, the last its summit, the keep.
TIERS = [[33, 15], [24, 20], [14, 24]]
# A corner block (MB-BASTION-CUBE-05), the right front one as drawn (at rest), its top, and the
# drum tower on it: its centre, radius and top; the front towers' turrets stand on it.
CORNER = [[NOTCH, -HALF], [HALF, -HALF], [HALF, -NOTCH], [NOTCH, -NOTCH]]
CORNER_TOP = 14
TOWER_AT = [35.5, -35.5]
TOWER_RADIUS = 7.5
TOWER_TOP = 23
# How far each corner block slides out at its transformation (diagonally, px across and along).
SLIDE_OUT = 13
# The gatehouse (MB-BASTION-CUBE-03): a block jutting out of the front face, its half width, its
# front edge and its top; the wall gun stands on its front.
GATE_HALF = 12
GATE_FRONT = -55
GATE_TOP = 16
WALL_GUN_AT = [0, -45]

# The front towers' turrets: two barrels side by side, firing their aimed bursts (BOSS-58).
TOWER_GUN = {"size": 4.6, "barrels": 2, "gap": 1.4, "bore": 1.1, "length": 7}
# The gatehouse's wall gun: five barrels side by side on a fixed base, all pointing straight down
# the screen, firing all five at once: a wall of bullets (MB-BASTION-CUBE-08).
WALL_GUN = {"size": 6, "barrels": 5, "gap": 4.4, "bore": 1.1, "length": 6, "turret": False}
# The keep's turret on the summit's front (the core's aimed shots, fans and bursts), and the crown
# rotor behind it (its last rings), under a hatch until then.
KEEP_GUN_AT = [0, -6]
KEEP_GUN = {"size": 4.8, "barrels": 3, "gap": 1.1, "bore": 1.1, "length": 7}
ROTOR_AT = [0, 6]
ROTOR = {"size": 4.4, "barrels": 8, "layout": "ring", "bore": 0.9, "length": 3.4}

_BASTION_CUBE = record({
    "id": "bastion-cube",
    # Its points and its parts' drops (MB-BASTION-CUBE-11).
    "stats": stats({
        "id": "bastion-cube",
        "name": "Bastion Cube",
        "size": 3.6,
        "coreRadius": 17,
        "coreHealth": 1000,
        "points": 3500,
        "groundSpeed": 0.6,
        "parts": [
            part("tower-left", [-TOWER_AT[0], TOWER_AT[1]], 11, 620),
            part("tower-right", [TOWER_AT[0], TOWER_AT[1]], 11, 620),
            part("gatehouse", [0, -43], 12, 720),
        ],
    }),
    # Where it stops and how it moves in place (MB-BASTION-CUBE-06): slow, heavy and square.
    "stopFraction": 0.72,
    "sway": {"amplitude": 60, "period": 8},
    "bob": {"amplitude": 5, "period": 4},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-BASTION-CUBE-03): a twin-barrelled turret on each front tower,
    # the wall gun on the gatehouse, and the core's: the keep turret on the summit and the crown
    # rotor behind it.
    "mounts": [
        gun_mount("tower-left", "tower-left", [-TOWER_AT[0], TOWER_AT[1]], TOWER_TOP, TOWER_GUN),
        gun_mount("tower-right", "tower-right", [TOWER_AT[0], TOWER_AT[1]], TOWER_TOP, TOWER_GUN),
        gun_mount("gatehouse", "gatehouse", WALL_GUN_AT, GATE_TOP, WALL_GUN),
        gun_mount("keep-gun", "core", KEEP_GUN_AT, TIERS[2][1], KEEP_GUN),
        gun_mount("crown-rotor", "core", ROTOR_AT, TIERS[2][1], ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-BASTION-CUBE-08): the gatehouse
    # drops a straight wall of five bullets, the front towers fire bursts of three at the player in
    # turn; the core adds an aimed shot, a straight fan, a burst, then the crown rotor's rings of 8,
    # turning half a step at each volley (a square grid, then the same turned 22.5°).
    "stages": stages(
        [
            volley.fan("gatehouse", 2.4, 5, 0, ORANGE, 1.6),
            volley.burst("tower-left", 2.6, 3, 0.12, RED, 1),
            volley.burst("tower-right", 2.6, 3, 0.12, RED, 2.3),
        ],
        [
            [volley.aimed("core", 3, 1, 0, MAGENTA, 1.4)],
            [volley.fan("core", 2.8, 5, 12, MAGENTA, 0.8)],
            [volley.burst("core", 2.2, 4, 0.13, MAGENTA, 0.6)],
            [
                volley.ring("core", 1.5, 8, 22.5, ORANGE, 0.4),
                volley.aimed("core", 2.4, 3, 12, MAGENTA, 1),
            ],
        ],
    ),
})

# Where the gatlings ride (MB-BASTION-CUBE-10): on the rear towers' tops once their blocks have slid
# out, and their pods' base and top.
REAR_TOWER_OUT = [TOWER_AT[0] + SLIDE_OUT, -TOWER_AT[1] + SLIDE_OUT]
GATLING_POD = [TOWER_TOP + 1, TOWER_TOP + 4.5]

# Its transformation (BOSS-45, MB-BASTION-CUBE-10): once both front towers are gone its four corner
# blocks slide out diagonally, opening the cube, and a gatling rides out on each rear tower. The
# summit hatch over its crown rotor bursts as the rotor comes into use, in its last stage
# (BOSS-58).
BASTION_CUBE = with_weapons(
    merge(_BASTION_CUBE, {"transformParts": [["tower-left", "tower-right"]]}),
    [
        hidden_weapon(
            "gatling-left",
            "gatling",
            [-REAR_TOWER_OUT[0], REAR_TOWER_OUT[1]],
            8,
            540,
            1,
            "red",
            1.2,
            GATLING_POD,
        ),
        hidden_weapon(
            "gatling-right",
            "gatling",
            [REAR_TOWER_OUT[0], REAR_TOWER_OUT[1]],
            8,
            540,
            1,
            "red",
            2.0,
            GATLING_POD,
        ),
    ],
    concat(
        concat(
            moving_region(
                "front-blocks",
                1,
                CORNER,
                slide([[0, 0, 0], [SLIDE_OUT, -SLIDE_OUT, 0]]),
                None,
                [0, 1000],
            ),
            moving_region(
                "rear-blocks",
                1,
                [[q[0], -q[1]] for q in CORNER],
                slide([[0, 0, 0], [SLIDE_OUT, SLIDE_OUT, 0]]),
                None,
                [0, 1000],
            ),
        ),
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
                "crown-rotor",
            ),
        ],
    ),
)
