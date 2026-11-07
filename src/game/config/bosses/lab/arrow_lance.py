# Copyright (c) 2026 Renaud Guillon
"""The Arrow Lance, the Lab's L-8 mini boss (specs/bosses/lab/L-8-arrow-lance.md).

A Lab boss, in the dev viewer only: no level brings it in. Offsets in px from the boss's centre,
X right and Y up (its nose points down, at -Y). A sleek stealth delta, a flat faceted arrowhead
pointing down the screen. 3 destroyable parts (BOSS-13): the laser pod on its nose and a gun pod
on each wingtip. Speed and precision: it sways fast and wide, firing quick aimed shots and narrow,
fast fans, while its nose laser aims at the player through its warning line and locks
(MB-ARROW-LANCE-08).
"""

import math

from game.config.bosses.boss_guns import gun_mount, laser_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# Its quick bullets: small and fast (MB-ARROW-LANCE-08).
DART = bullet("orange", 235, 3.5)
NEEDLE = bullet("red", 225, 3.5)
RING = bullet("orange", 165)

# MB-ARROW-LANCE-01: the delta's right half seen from above, from its nose round its leading edge
# to its wingtip and back along its sawtooth trailing edge to the centre line.
DELTA = [  # type: list[list[float]]
    [0, -56],
    [51, 22],
    [41, 29],
    [29, 21],
    [17, 29],
    [0, 23],
]

# The nose's laser: an emitter on a turret that follows the player through its warning line, then
# locks (BOSS-30, BOSS-31; MB-ARROW-LANCE-03).
NOSE_LASER = {"size": 4.2, "bore": 1.8, "length": 11, "turret": True}
# A wingtip pod's turret: two long, thin barrels side by side, taking turns through its fans.
WING_GUN = {"size": 4.2, "barrels": 2, "gap": 2.6, "bore": 0.9, "length": 9}

# Where its parts stand: the nose pod on the arrow's point, a pod on each wingtip.
NOSE_AT = [0, -36]
# The top of the nose pod, the laser turret stands on.
NOSE_TOP = 8
WING_AT = [36, 14]
WING_TOP = 5
# The core's dorsal turret on its spine, and the rotor under a hatch on its back (BOSS-58).
SPINE_AT = [0, -12]
ROTOR_AT = [0, 15]
# The top of the spine the core's guns stand on.
SPINE_TOP = 9

_ARROW_LANCE = record({
    "id": "arrow-lance",
    # Its points and its parts' drops (MB-ARROW-LANCE-11).
    "stats": stats({
        "id": "arrow-lance",
        "name": "Arrow Lance",
        "size": 3.2,
        "coreRadius": 16,
        "coreHealth": 1300,
        "points": 4000,
        "groundSpeed": 1.3,
        "parts": [
            part("nose", NOSE_AT, 11, 680),
            part("wing-left", [-WING_AT[0], WING_AT[1]], 11, 660),
            part("wing-right", WING_AT, 11, 660),
        ],
    }),
    # Where it stops and how it moves in place (MB-ARROW-LANCE-06): fast and wide.
    "stopFraction": 0.74,
    "sway": {"amplitude": 90, "period": 4.2},
    "bob": {"amplitude": 6, "period": 2.4},
    "guns": {},
    # It transforms once both wingtip pods are gone (MB-ARROW-LANCE-10).
    "transformParts": [["wing-left", "wing-right"]],
    # Its gun mounts (BOSS-58, MB-ARROW-LANCE-03): the laser turret on the nose pod, a twin gun on
    # each wingtip pod, and the core's: a fan turret on its spine (its aimed shots, bursts and
    # fans) and a rotor on its back under a hatch (its last ring).
    "mounts": [
        laser_mount("nose", "nose", NOSE_AT, NOSE_TOP, NOSE_LASER),
        gun_mount("wing-left", "wing-left", [-WING_AT[0], WING_AT[1]], WING_TOP, WING_GUN),
        gun_mount("wing-right", "wing-right", WING_AT, WING_TOP, WING_GUN),
        gun_mount(
            "spine",
            "core",
            SPINE_AT,
            SPINE_TOP,
            {"size": 4.6, "barrels": 3, "gap": 1, "bore": 0.9, "length": 7},
        ),
        gun_mount(
            "tail-rotor",
            "core",
            ROTOR_AT,
            SPINE_TOP,
            {"size": 4.4, "barrels": 10, "layout": "ring", "bore": 0.8, "length": 3},
        ),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-ARROW-LANCE-08). The wingtips' fans
    # are narrow (6°) and fast; the spine turret's fans 5° apart.
    "stages": stages(
        [
            volley.laser("nose", 4.6, 1.1, 2.2),
            volley.aimed("wing-left", 2.2, 3, 6, DART, 0.9),
            volley.aimed("wing-right", 2.2, 3, 6, DART, 2.0),
        ],
        [
            [volley.aimed("core", 1.5, 1, 0, NEEDLE, 0.6)],
            [volley.burst("core", 2, 3, 0.1, NEEDLE, 0.6)],
            [volley.aimed("core", 1.6, 5, 5, NEEDLE, 0.6)],
            [
                merge(volley.ring("core", 1.6, 10, 8, RING, 0.4), {"mount": "tail-rotor"}),
                volley.aimed("core", 1.6, 1, 0, NEEDLE, 1.2),
            ],
        ],
    ),
})

# The stealth panels over its mid-wings (MB-ARROW-LANCE-05), the right one: a faceted plate behind
# the leading edge, the mortars under it; mirrored across the centre line.
WING_PANEL = [[11, -16], [22, -16], [33, 8], [30, 13], [11, 13]]  # type: list[list[float]]
# Their heights: over the wing's top, under the leading edge's chine.
PANEL_HEIGHTS = [2.5, 7]

# Its transformation (D-224, MB-ARROW-LANCE-10): once both wingtip pods are gone its wing panels
# burst off, baring a dark metal frame, and a pair of mortars unfold on it: slow, heavy flak shells
# from a fast craft.
ARROW_LANCE = with_weapons(
    _ARROW_LANCE,
    [
        hidden_weapon("mortar-left", "mortar", [-21, -1], 9, 540, 1, "red", 1.2, [2.5, 6.5]),
        hidden_weapon("mortar-right", "mortar", [21, -1], 9, 540, 1, "red", 2.0, [2.5, 6.5]),
    ],
    [
        armour_region("panels", 1, WING_PANEL, "wing", PANEL_HEIGHTS),
        # The hatch over its back rotor (BOSS-58): it bursts as the rotor comes into use, in its
        # last stage, and the rotor rises out of it.
        armour_region(
            "rotor-hatch",
            None,
            [
                [6 * math.cos(k * math.pi / 4), ROTOR_AT[1] + 6 * math.sin(k * math.pi / 4)]
                for k in range(8)
            ],
            "ring",
            None,
            False,
            "tail-rotor",
        ),
    ],
)
