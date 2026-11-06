# Copyright (c) 2026 Renaud Guillon
"""The Twin-Boom Lancer, the Lab's L-18 mini boss (specs/bosses/lab/L-18-twin-boom-lancer.md).

Lab boss: in the dev viewer only, no level brings it in. A gigantic twin-boom fighter seen from
above: a central pod with its cockpit on a straight wing, two long engine booms either side of
it, an engine cowling at the front of each, a tail fin at the back of each, and a tailplane joining
them. Its two boom guns fire two parallel streams straight down, its dorsal turret aimed bursts.
Once both boom guns are gone it morphs (MB-TWIN-BOOM-LANCER-10): its tailplane splits and folds up,
its inner wings telescope away, its two booms slide inward and forward and lock together under the
pod into one long heavy gun body, their engine cowlings peel open in petals and a heavy cannon
rises out of each, their fins and the folded tailplane standing over the merged tail as cooling
fins. From two streams to heavy concentrated shells.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide
from game.config.record import concat, merge, record

# MB-TWIN-BOOM-LANCER-01: the central pod along Y, `[y, half width, belly, top]` stations from its
# nose to its tail.
POD = [  # type: list[list[float]]
    [-46, 0.6, 22, 23],
    [-42, 4.2, 18, 27],
    [-34, 7.5, 16, 31],
    [-20, 9.5, 15, 33],
    [0, 10, 15, 33],
    [12, 8.5, 16, 31],
    [22, 4.5, 19, 26],
    [26, 0.6, 22, 23],
]


def pod_top(y: float) -> float:
    """Return the height of the pod's top at `y`, between its stations (0 off its ends)."""
    for k in range(len(POD) - 1):
        a = POD[k]
        b = POD[k + 1]
        if a[0] <= y <= b[0]:
            return a[3] + (b[3] - a[3]) * (y - a[0]) / (b[0] - a[0])
    return 0


# MB-TWIN-BOOM-LANCER-02: the booms as drawn (the right one; the left is its mirror image): their
# axis's X and height, their radius, and `[front, back]` (the cowling's front to the tail's end).
BOOM_X = 30
BOOM_H = 12
BOOM_R = 6
BOOM_ENDS = [-47, 56]
# The engine cowling at a boom's front, `[front, back]`, and its radius: its upper half peels open
# in three petals (the view rig), the lower half stays on the boom.
COWL = [-47, -30]
COWL_R = 8
# The straight wing: its chord `[leading, trailing]` at the root and at its tip, its tip's X, and
# its heights `[bottom, top]`. The outer panels ride the booms; the inner ones (between the pod and
# a boom) telescope away (the view rig).
WING_ROOT = [-18, -3]
WING_TIP = [-15, -6]
WING_SPAN = 64
WING_Y = [12.6, 15.6]
# The tailplane joining the booms' tails: its chord and height; each half folds up about its root
# on its boom's inner side (the view rig).
TAILPLANE = [42, 52]
TAILPLANE_H = 14.6
# The tail fins standing on the booms' tails: their chord at the root and their top.
FIN = [38, 55]
FIN_TOP = 31
# MB-TWIN-BOOM-LANCER-10: how far each boom slides to lock against the other under the pod (the
# right one: in to X 8, forward 16 px).
LOCK = [8.0 - BOOM_X, -16.0]

RED = bullet("red", 190)
ORANGE = bullet("orange", 200)
GOLD = bullet("orange", 175)
BLUE = bullet("blue", 180)

# Its guns (BOSS-58, MB-TWIN-BOOM-LANCER-03): a fixed twin-barrelled gun pack on each boom behind
# its cowling, pointing down the screen (the barrels taking turns: a stream); a three-barrelled
# turret on the pod's back; the core's: a twin-barrelled turret on the pod's nose and a rotor on
# its tail (its last rings), under a hatch until then.
BOOM_GUN_AT = [BOOM_X, -22]
BOOM_GUN_H = 21
BOOM_GUN = {"size": 4, "barrels": 2, "gap": 2.8, "bore": 1, "length": 11, "turret": False}
DORSAL_AT = [0, -6]
DORSAL_H = 34.5
DORSAL_GUN = {"size": 4.8, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 7.5}
NOSE_AT = [0, -37]
NOSE_H = math.floor(pod_top(-37) * 10) / 10
NOSE_GUN = {"size": 4.2, "barrels": 2, "gap": 2.8, "bore": 1, "length": 7}
ROTOR_AT = [0, 13]
ROTOR_H = math.floor(pod_top(13) * 10) / 10
ROTOR = {"size": 4.4, "barrels": 12, "layout": "ring", "bore": 0.75, "length": 3.2}

_TWIN_BOOM_LANCER = record({
    "id": "twin-boom-lancer",
    # Its points and its parts' drops (MB-TWIN-BOOM-LANCER-11).
    "stats": stats({
        "id": "twin-boom-lancer",
        "name": "Twin-Boom Lancer",
        "size": 3.6,
        "coreRadius": 14,
        "coreHealth": 1200,
        "points": 4300,
        "groundSpeed": 1.2,
        "parts": [
            part("boom-left", [-BOOM_GUN_AT[0], BOOM_GUN_AT[1]], 9, 640),
            part("boom-right", BOOM_GUN_AT, 9, 640),
            part("dorsal", DORSAL_AT, 10, 720),
        ],
    }),
    # Where it stops and how it moves in place (MB-TWIN-BOOM-LANCER-06): a fighter's quick sways,
    # strafing its two streams across the screen.
    "stopFraction": 0.74,
    "sway": {"amplitude": 66, "period": 6.4},
    "bob": {"amplitude": 8, "period": 3},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-TWIN-BOOM-LANCER-03).
    "mounts": [
        gun_mount(
            "boom-left", "boom-left", [-BOOM_GUN_AT[0], BOOM_GUN_AT[1]], BOOM_GUN_H, BOOM_GUN
        ),
        gun_mount("boom-right", "boom-right", BOOM_GUN_AT, BOOM_GUN_H, BOOM_GUN),
        gun_mount("dorsal", "dorsal", DORSAL_AT, DORSAL_H, DORSAL_GUN),
        gun_mount("nose-gun", "core", NOSE_AT, NOSE_H, NOSE_GUN),
        gun_mount("tail-rotor", "core", ROTOR_AT, ROTOR_H, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-TWIN-BOOM-LANCER-08): two parallel
    # streams straight down from the boom guns (one bullet at a time, their barrels taking turns)
    # and the dorsal turret's aimed bursts; the core's aimed shots, spreads and fans, then the tail
    # rotor's rings of 12.
    "stages": stages(
        [
            volley.fan("boom-left", 0.55, 1, 0, ORANGE, 0.6),
            volley.fan("boom-right", 0.55, 1, 0, ORANGE, 0.85),
            volley.burst("dorsal", 2.4, 3, 0.13, RED, 1.4),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, BLUE, 1.5)],
            [volley.aimed("core", 2.4, 3, 8, BLUE, 1)],
            [volley.fan("core", 2.4, 5, 12, GOLD, 0.8)],
            [
                volley.ring("core", 1.6, 12, 8, BLUE, 0.4),
                volley.aimed("core", 2.6, 2, 6, RED, 1.2),
            ],
        ],
    ),
})


def boom_outline() -> list[list[float]]:
    """Return the right boom's moving piece as drawn (MB-TWIN-BOOM-LANCER-05).

    Its cowling, its boom down to its tail and its outer wing panel, from its front inner corner
    round.
    """
    x0 = BOOM_X - COWL_R - 0.5
    x1 = BOOM_X + COWL_R + 0.5
    xb = BOOM_X + BOOM_R + 1
    return [
        [x0, BOOM_ENDS[0] - 1],
        [x1, BOOM_ENDS[0] - 1],
        [x1, COWL[1]],
        [xb, COWL[1]],
        [xb, WING_ROOT[0]],
        [WING_SPAN + 1, WING_TIP[0] - 0.5],
        [WING_SPAN + 1, WING_TIP[1] + 0.5],
        [xb, WING_ROOT[1]],
        [xb, BOOM_ENDS[1] + 1],
        [BOOM_X - BOOM_R - 1, BOOM_ENDS[1] + 1],
        [BOOM_X - BOOM_R - 1, COWL[1]],
        [x0, COWL[1]],
    ]


# Where the cannons stand (MB-TWIN-BOOM-LANCER-10): in the opened cowlings at the merged booms'
# front, drawn at `CANNON_DRAWN` on the boom as it rests; their pods' base and top, inside the
# cowling.
CANNON_DRAWN = [BOOM_X, -39]
CANNON_AT = [CANNON_DRAWN[0] + LOCK[0], CANNON_DRAWN[1] + LOCK[1]]
CANNON_POD = [BOOM_H + 5, BOOM_H + 8]
BOOM_SLIDE = slide([[0, 0, 0], [LOCK[0], LOCK[1], 0]])

# Its transformation (BOSS-45, MB-TWIN-BOOM-LANCER-10): once both boom guns are gone its booms
# slide in and lock together under the pod, a cannon rising out of each opened cowling (riding its
# boom). The hatch over its tail rotor bursts as the rotor comes into use, in its last stage
# (BOSS-58).
TWIN_BOOM_LANCER = with_weapons(
    merge(_TWIN_BOOM_LANCER, {"transformParts": [["boom-left", "boom-right"]]}),
    [
        hidden_weapon(
            "cannon-left",
            "cannon",
            [-CANNON_AT[0], CANNON_AT[1]],
            7,
            580,
            1,
            "orange",
            1.2,
            CANNON_POD,
            [0, 0, 0],
        ),
        hidden_weapon(
            "cannon-right",
            "cannon",
            CANNON_AT,
            7,
            580,
            1,
            "orange",
            2.0,
            CANNON_POD,
            [0, 0, 0],
        ),
    ],
    concat(
        moving_region("boom", 1, boom_outline(), BOOM_SLIDE, None, [2, 1000]),
        [
            armour_region(
                "rotor-hatch",
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
                "tail-rotor",
            ),
        ],
    ),
)
