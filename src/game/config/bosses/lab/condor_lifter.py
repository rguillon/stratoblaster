# Copyright (c) 2026 Renaud Guillon
"""The Condor Lifter, the Lab's L-16 mini boss (specs/bosses/lab/L-16-condor-lifter.md).

Lab boss: in the dev viewer only, no level brings it in. A gigantic heavy-lift cargo plane seen
from above: a fat fuselage, a high straight wing with four turboprops, a T-tail over a rear cargo
ramp, and two containers strapped on an external cargo deck on its back. It crosses aimed fire
from its two outer turboprops' guns over the player, with bursts from its nose gun. Once both
engine guns are gone it morphs: its cargo ramp drops open, the containers' roofs blow off, their
walls hinge down flat into gun decks and their cargo telescopes out into barrels: a pair of
batteries, walls of wide fans straight down.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# MB-CONDOR-LIFTER-01: the fuselage, a fat loft along Y: at stations from its nose (-Y) to its
# flat rear (the cargo ramp's door), `[y, half width, floor, top]`.
FUSELAGE = [  # type: list[list[float]]
    [-62, 0, 10, 10],
    [-60, 5, 5.5, 14],
    [-55, 8.5, 3.5, 18],
    [-46, 11, 2, 20],
    [30, 11, 2, 20],
    [38, 10, 4, 19.5],
    [44, 8.5, 6, 19],
]


def fuselage_at(y: float) -> list[float]:
    """Return the fuselage's `[half width, floor, top]` at `y` (zeros off its ends)."""
    for k in range(len(FUSELAGE) - 1):
        a = FUSELAGE[k]
        b = FUSELAGE[k + 1]
        if a[0] <= y <= b[0]:
            u = (y - a[0]) / (b[0] - a[0])
            return [a[i] + (b[i] - a[i]) * u for i in [1, 2, 3]]
    return [0, 0, 0]


# The high straight wing (MB-CONDOR-LIFTER-02): its leading and trailing edges at the root and at
# the tip `[y0, y1]`, its tip's X, its underside and top.
WING_ROOT = [-15, 3]
WING_TIP = [-12, 0]
WING_SPAN = 62
WING_LOW = 19.5
WING_TOP = 22.5
# The four turboprops over the wing: their X, their front and back, radius and axis height; the
# propellers ahead of them (their rig): the hub's Y and the blades' reach.
NACELLE_X = [22, 42]
NACELLE_Y = [-27, 6]
NACELLE_R = 4.2
NACELLE_H = WING_TOP + 3
PROP_Y = -29
PROP_R = 8.5
# The T-tail: the fin's root chord along the centre line, its top's chord and height; the
# tailplane on its top, its root and tip chords and its tip's X.
FIN_ROOT = [32, 50]
FIN_TIP = [42, 51]
FIN_TOP = 44
TAIL_ROOT = [42, 52]
TAIL_TIP = [47, 52]
TAIL_SPAN = 24
# The cargo ramp at the fuselage's flat rear: its hinge (along X at the rear's foot), its width
# and length (up the rear door, closed).
RAMP_Y = 44
RAMP_H = 6
RAMP_HALF = 8
RAMP_LENGTH = 13
# The external cargo deck on its back, `[y0, y1]`, its half width and top; the containers strapped
# on it (the right one; mirrored), `[x0, x1]` and `[y0, y1]`, and their roofs' height.
DECK_Y = [5, 31]
DECK_HALF = 19
DECK_TOP = 21.4
CONTAINER_X = [4, 17]
CONTAINER_Y = [7, 29]
CONTAINER_TOP = DECK_TOP + 8

RED = bullet("red", 190)
TEAL = bullet("blue", 180)
ORANGE = bullet("orange", 180)

# Its guns (BOSS-58, MB-CONDOR-LIFTER-03): twin barrels on each outer turboprop's back, three on
# the nose gun's turret, and the core's: a twin-barrelled turret on the wing's centre section and
# a rotor behind the cockpit (its last rings), under a hatch until then.
ENGINE_GUN_AT = [42, -13]
ENGINE_GUN_H = NACELLE_H + NACELLE_R + 0.6
ENGINE_GUN = {"size": 3.8, "barrels": 2, "gap": 2.6, "bore": 0.9, "length": 7}
NOSE_GUN_AT = [0, -47]
NOSE_GUN_H = math.floor(fuselage_at(-47)[2] + 0.5)
NOSE_GUN = {"size": 4.4, "barrels": 3, "gap": 1.2, "bore": 1, "length": 7.5}
DORSAL_AT = [0, -5]
DORSAL_H = WING_TOP + 0.5
DORSAL_GUN = {"size": 4.6, "barrels": 2, "gap": 3, "bore": 1.1, "length": 7.5}
ROTOR_AT = [0, -33]
ROTOR_H = 20.5
ROTOR = {"size": 4.2, "barrels": 10, "layout": "ring", "bore": 0.8, "length": 3.4}

_CONDOR_LIFTER = record({
    "id": "condor-lifter",
    # Its points and its parts' drops (MB-CONDOR-LIFTER-12).
    "stats": stats({
        "id": "condor-lifter",
        "name": "Condor Lifter",
        "size": 3.7,
        "coreRadius": 16,
        "coreHealth": 1100,
        "points": 3800,
        "groundSpeed": 1.1,
        "parts": [
            part("engine-left", [-NACELLE_X[1], -12], 10, 560),
            part("engine-right", [NACELLE_X[1], -12], 10, 560),
            part("nose-gun", [0, -48], 10, 640),
        ],
    }),
    # Where it stops and how it moves in place (MB-CONDOR-LIFTER-06): a heavy lifter, long slow
    # sways.
    "stopFraction": 0.72,
    "sway": {"amplitude": 55, "period": 8.5},
    "bob": {"amplitude": 5, "period": 3.4},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-CONDOR-LIFTER-03).
    "mounts": [
        gun_mount(
            "engine-left",
            "engine-left",
            [-ENGINE_GUN_AT[0], ENGINE_GUN_AT[1]],
            ENGINE_GUN_H,
            ENGINE_GUN,
        ),
        gun_mount("engine-right", "engine-right", ENGINE_GUN_AT, ENGINE_GUN_H, ENGINE_GUN),
        gun_mount("nose-gun", "nose-gun", NOSE_GUN_AT, NOSE_GUN_H, NOSE_GUN),
        gun_mount("dorsal", "core", DORSAL_AT, DORSAL_H, DORSAL_GUN),
        gun_mount("cargo-rotor", "core", ROTOR_AT, ROTOR_H, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-CONDOR-LIFTER-08): the outer
    # turboprops' aimed pairs cross over the player from far apart, the nose gun's bursts; the
    # core's aimed shots and spreads, then fans 12 degrees apart, ending in the rotor's rings of 10.
    "stages": stages(
        [
            volley.aimed("engine-left", 1.8, 2, 5, RED, 0.6),
            volley.aimed("engine-right", 1.8, 2, 5, RED, 1.5),
            volley.burst("nose-gun", 2.4, 3, 0.12, ORANGE, 1.1),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, TEAL, 1.6)],
            [volley.aimed("core", 2.6, 3, 9, TEAL, 1)],
            [volley.fan("core", 2.6, 5, 12, ORANGE, 0.8)],
            [
                volley.ring("core", 1.5, 10, 9, TEAL, 0.4),
                volley.aimed("core", 2.6, 2, 6, RED, 1.2),
            ],
        ],
    ),
})

# Where the batteries stand (MB-CONDOR-LIFTER-10): in the containers, on the cargo deck; their
# pods' base (the deck) and top.
BATTERY_AT = [10.5, 18]
BATTERY_POD = [DECK_TOP, DECK_TOP + 2.4]
# The containers' outline (the right one; mirrored): the region their roofs blow off.
CONTAINER = [
    [CONTAINER_X[0], CONTAINER_Y[0]],
    [CONTAINER_X[1], CONTAINER_Y[0]],
    [CONTAINER_X[1], CONTAINER_Y[1]],
    [CONTAINER_X[0], CONTAINER_Y[1]],
]

# Its transformation (MB-CONDOR-LIFTER-10): once both engine guns are gone its cargo ramp drops
# open, the containers' roofs blow off, their walls hinge down flat into gun decks and a battery
# rises out of each, its cargo telescoping into barrels (its view rig). The hatch over the cargo
# rotor bursts as the rotor comes into use, in its last stage (BOSS-58).
CONDOR_LIFTER = with_weapons(
    merge(_CONDOR_LIFTER, {"transformParts": [["engine-left", "engine-right"]]}),
    [
        hidden_weapon(
            "battery-left",
            "battery",
            [-BATTERY_AT[0], BATTERY_AT[1]],
            7.5,
            510,
            1,
            "blue",
            1.2,
            BATTERY_POD,
            [0, 0, 0],
        ),
        hidden_weapon(
            "battery-right",
            "battery",
            BATTERY_AT,
            7.5,
            510,
            1,
            "blue",
            2.0,
            BATTERY_POD,
            [0, 0, 0],
        ),
    ],
    [
        armour_region("containers", 1, CONTAINER, "shell", [DECK_TOP - 0.2, CONTAINER_TOP + 1]),
        armour_region(
            "rotor-hatch",
            None,
            [
                [
                    ROTOR_AT[0] + 5.5 * math.cos(k * math.pi / 4 + math.pi / 8),
                    ROTOR_AT[1] + 5.5 * math.sin(k * math.pi / 4 + math.pi / 8),
                ]
                for k in range(8)
            ],
            "ring",
            None,
            False,
            "cargo-rotor",
        ),
    ],
)
