# Copyright (c) 2026 Renaud Guillon
"""The Rotor Bastion, the Lab's L-13 mini boss (specs/bosses/lab/L-13-rotor-bastion.md).

Lab boss: in the dev viewer only, no level brings it in. A flying tower held up by four huge
ducted rotors on outrigger arms (a quad-rotor fortress): a square armoured tower in the middle, an
armoured prow on its front, a rotor duct at the end of each arm. Its two front rotor hubs carry gun
pods that fire a crossfire from far out on its flanks; the tower's crown turret fans straight down.
Once both front gun pods are gone its front arms fold back against the tower's flanks (it changes
shape, BOSS-45), its prow's armour bursts open and an orb rises on each side of it: from spread-out
crossfire to a compact, spinning storm of rings.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, swing
from game.config.record import concat, merge, record

DEG = math.pi / 180

RED = bullet("red", 185)
ORANGE = bullet("orange", 175)
MAGENTA = bullet("magenta", 190)

# MB-ROTOR-BASTION-01: the tower's half width, its walls' top and its roof's parapet top.
TOWER_HALF = 15
TOWER_WALL = 20
TOWER_ROOF = 22
# A rotor duct (MB-ROTOR-BASTION-05): its outer and inner radius and its rim's low and high edge.
DUCT_OUT = 13
DUCT_IN = 10.6
DUCT_LOW = 4
DUCT_HIGH = 10
# The motor nacelle on a duct's hub: its radius and top.
HUB_RADIUS = 4.2
HUB_TOP = 14.4
# The front ducts' centres at rest, and the rear ducts'.
FRONT_DUCT = [40, -31]
REAR_DUCT = [41, 36]
# The front arms' hinge, on the tower's front corner, and how far they fold back about it (degrees,
# counter-clockwise seen from above for the right one): their ducts end up beside the tower's
# flanks.
ARM_PIVOT = [TOWER_HALF, -TOWER_HALF]
FOLD = 84
# The arms' beams: their height.
ARM_LOW = 5.5
ARM_HIGH = 9.5
# The prow (MB-ROTOR-BASTION-10): the armoured bow on the tower's front, its outline and top.
PROW = [
    [-TOWER_HALF, -TOWER_HALF + 1],
    [TOWER_HALF, -TOWER_HALF + 1],
    [12, -29],
    [6, -33],
    [-6, -33],
    [-12, -29],
]
PROW_TOP = 14
# The rear balcony (the core's gun): its depth behind the tower and its top.
BALCONY_BACK = 25
BALCONY_TOP = 11

# The front gun pods' turrets: two barrels side by side, sweeping their aimed spreads (BOSS-58).
POD_GUN = {"size": 4.4, "barrels": 2, "gap": 2.9, "bore": 1.1, "length": 7}
POD_GUN_HEIGHT = 15
# The crown turret on the roof's front: three barrels, sweeping its fans straight down.
CROWN_AT = [0, -4]
CROWN_GUN = {"size": 5, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 7.5}
CROWN_GUN_HEIGHT = 25
# The core's guns: the balcony turret behind the tower, and the roof rotor (its last rings), under
# a hatch on the roof's back until then.
BALCONY_GUN_AT = [0, 20]
BALCONY_GUN = {"size": 4.6, "barrels": 3, "gap": 1.1, "bore": 1.1, "length": 7}
ROTOR_AT = [0, 9]
ROTOR = {"size": 4.4, "barrels": 12, "layout": "ring", "bore": 0.7, "length": 3.2}


def _duct_outline(cx: float, cy: float, r: float) -> list[list[float]]:
    """Return an octagon `r` px round `(cx, cy)`, flat sides facing the axes."""
    return [
        [cx + r * math.cos(DEG * (22.5 + 45 * k)), cy + r * math.sin(DEG * (22.5 + 45 * k))]
        for k in range(8)
    ]


def front_arm() -> list[list[float]]:
    """Return the right front arm's outline at rest (MB-ROTOR-BASTION-05): its duct and its beam.

    From the tower's front corner out to the duct, round the duct's outer side.
    """
    r = DUCT_OUT + 1
    cx = FRONT_DUCT[0]
    cy = FRONT_DUCT[1]
    duct = _duct_outline(cx, cy, r)
    return [
        [ARM_PIVOT[0] - 0.5, ARM_PIVOT[1] + 0.5],
        [ARM_PIVOT[0] + 3, ARM_PIVOT[1] + 3],
        duct[2],
        duct[1],
        duct[0],
        duct[7],
        duct[6],
        duct[5],
        duct[4],
        [ARM_PIVOT[0] - 0.5, ARM_PIVOT[1] - 3],
    ]


ARM_SWING = swing([ARM_PIVOT[0], ARM_PIVOT[1], 0], "up", [0, FOLD])
_ROTOR_BASTION = record({
    "id": "rotor-bastion",
    # Its points and its parts' drops (MB-ROTOR-BASTION-11).
    "stats": stats({
        "id": "rotor-bastion",
        "name": "Rotor Bastion",
        "size": 3.8,
        "coreRadius": 16,
        "coreHealth": 1050,
        "points": 3600,
        "groundSpeed": 0.8,
        "parts": [
            part("rotor-left", [-FRONT_DUCT[0], FRONT_DUCT[1]], 11, 640),
            part("rotor-right", FRONT_DUCT, 11, 640),
            part("crown", CROWN_AT, 9, 700),
        ],
    }),
    # Where it stops and how it moves in place (MB-ROTOR-BASTION-06): a hovering, drifting craft.
    "stopFraction": 0.72,
    "sway": {"amplitude": 50, "period": 7},
    "bob": {"amplitude": 7, "period": 3.2},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-ROTOR-BASTION-03): a twin-barrelled turret on each front rotor's
    # hub, the crown turret on the roof, and the core's: the balcony turret behind the tower and
    # the roof rotor.
    "mounts": [
        gun_mount(
            "rotor-left",
            "rotor-left",
            [-FRONT_DUCT[0], FRONT_DUCT[1]],
            POD_GUN_HEIGHT,
            POD_GUN,
        ),
        gun_mount("rotor-right", "rotor-right", FRONT_DUCT, POD_GUN_HEIGHT, POD_GUN),
        gun_mount("crown", "crown", CROWN_AT, CROWN_GUN_HEIGHT, CROWN_GUN),
        gun_mount("balcony-gun", "core", BALCONY_GUN_AT, BALCONY_TOP, BALCONY_GUN),
        gun_mount("roof-rotor", "core", ROTOR_AT, TOWER_ROOF, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-ROTOR-BASTION-08): the front pods
    # fire aimed spreads of 3 from far out on each side (a crossfire), the crown fans 5 straight
    # down; the core adds an aimed shot, a burst, an aimed spread, then the roof rotor's rings of
    # 12.
    "stages": stages(
        [
            volley.aimed("rotor-left", 2.4, 3, 8, RED, 1),
            volley.aimed("rotor-right", 2.4, 3, 8, RED, 2.2),
            volley.fan("crown", 2.8, 5, 14, ORANGE, 1.6),
        ],
        [
            [volley.aimed("core", 2.6, 1, 0, MAGENTA, 1.3)],
            [volley.burst("core", 2.4, 3, 0.14, MAGENTA, 0.8)],
            [volley.aimed("core", 2.6, 4, 10, MAGENTA, 0.8)],
            [
                volley.ring("core", 1.6, 12, 15, ORANGE, 0.4),
                volley.burst("core", 2.6, 3, 0.13, MAGENTA, 1.2),
            ],
        ],
    ),
})

# Where the orbs rise (MB-ROTOR-BASTION-10): either side of the prow, on its bared frame, and
# their pods' base and top.
ORB_AT = [6.5, -23]
ORB_POD = [3, 6.5]

# Its transformation (BOSS-45, MB-ROTOR-BASTION-10): once both front gun pods are gone its front
# arms fold back against the tower's flanks, and the prow's armour bursts off on a pair of orbs.
# The roof hatch over its rotor bursts as the rotor comes into use, in its last stage (BOSS-58).
ROTOR_BASTION = with_weapons(
    merge(_ROTOR_BASTION, {"transformParts": [["rotor-left", "rotor-right"]]}),
    [
        hidden_weapon(
            "orb-left", "orb", [-ORB_AT[0], ORB_AT[1]], 6.5, 560, 1, "orange", 1.2, ORB_POD
        ),
        hidden_weapon("orb-right", "orb", ORB_AT, 6.5, 560, 1, "orange", 2.0, ORB_POD),
    ],
    concat(
        moving_region("front-arm", 1, front_arm(), ARM_SWING, None, [0, 1000]),
        [
            armour_region("prow", 1, PROW, "shell", [2, PROW_TOP], False),
            armour_region(
                "roof-hatch",
                None,
                [
                    [
                        ROTOR_AT[0] + 5.6 * math.cos(k * math.pi / 4 + math.pi / 8),
                        ROTOR_AT[1] + 5.6 * math.sin(k * math.pi / 4 + math.pi / 8),
                    ]
                    for k in range(8)
                ],
                "ring",
                None,
                False,
                "roof-rotor",
            ),
        ],
    ),
)
