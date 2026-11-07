# Copyright (c) 2026 Renaud Guillon
"""The Gale Corvette, the Lab's L-11 mini boss (specs/bosses/lab/L-11-gale-corvette.md).

Lab boss: in the dev viewer only, no level brings it in. A small, fast armed airship seen from
above: a riveted cigar gas envelope over a long gondola whose nose juts out ahead of it, tail fins
at its stern, and an engine nacelle on an outrigger each side, its pusher propeller behind it. It
chases the player with aimed fire: bursts from the bow gun, aimed pairs from the engine guns.
Once both engine guns are gone it turns round (BOSS-46) to bring its stern to bear, its
propellers swivelling up into lift rotors (its view rig), and the fairings over its stern fins
burst off on a pair of batteries: it fights on as a rear guard, walls of fans straight down.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# MB-GALE-CORVETTE-01: the gas envelope, a cigar along Y: its axis's height, and its radius at
# stations from its nose (-Y) to its tail, `[y, radius]`.
ENV_H = 22
ENVELOPE = [  # type: list[list[float]]
    [-44, 0],
    [-42, 4.5],
    [-37, 8.5],
    [-29, 11.5],
    [-17, 13],
    [6, 13],
    [20, 11.5],
    [32, 8],
    [42, 4],
    [46, 0],
]


def envelope_radius(y: float) -> float:
    """Return the envelope's radius at `y` (0 off its ends), between its stations."""
    for k in range(len(ENVELOPE) - 1):
        a = ENVELOPE[k]
        b = ENVELOPE[k + 1]
        if a[0] <= y <= b[0]:
            return a[1] + (b[1] - a[1]) * (y - a[0]) / (b[0] - a[0])
    return 0


def envelope_top(y: float) -> float:
    """Return the height of the envelope's top at `y`."""
    return ENV_H + envelope_radius(y)


# The gondola under it (MB-GALE-CORVETTE-02): from its nose (jutting out ahead of the envelope) to
# its tail, its half width, its floor and its deck.
GONDOLA = [-62, 14]
GONDOLA_HALF = 6
GONDOLA_LOW = 3
GONDOLA_TOP = 11
# The engine nacelles on their outriggers: their centre, half length, radius and axis height.
NACELLE_AT = [36, 2]
NACELLE_HALF = 11
NACELLE_RADIUS = 4.5
NACELLE_H = 17
# The pusher propeller behind each nacelle: its hub's Y, its blades' reach.
PROP_Y = NACELLE_AT[1] + NACELLE_HALF + 4
PROP_RADIUS = 8
# The stern fins: the horizontal stabilisers' root and tip chords `[y0, y1]`, their tip's X and
# their top; the batteries ride on them under fairings (MB-GALE-CORVETTE-10).
FIN_ROOT = [28, 47]
FIN_TIP = [37, 46]
FIN_SPAN = 26
FIN_TOP = ENV_H + 0.6

RED = bullet("red", 190)
ORANGE = bullet("orange", 180)
BLUE = bullet("blue", 175)

# Its guns (BOSS-58, MB-GALE-CORVETTE-03): three barrels on the bow gun's turret, twin barrels on
# each engine gun, and the core's: a twin-barrelled dorsal turret on the envelope's back and a
# rotor behind it (its last rings), under a hatch until then.
BOW_GUN_AT = [0, -54]
BOW_GUN = {"size": 4.6, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 8}
ENGINE_GUN_AT = [36, -3]
ENGINE_GUN_H = NACELLE_H + NACELLE_RADIUS + 0.8
ENGINE_GUN = {"size": 4, "barrels": 2, "gap": 2.8, "bore": 1, "length": 7}
DORSAL_AT = [0, -15]
DORSAL_H = math.floor(envelope_top(-15))
DORSAL_GUN = {"size": 4.6, "barrels": 2, "gap": 3, "bore": 1.1, "length": 7.5}
ROTOR_AT = [0, 15]
ROTOR_H = math.floor(envelope_top(15))
ROTOR = {"size": 4.2, "barrels": 10, "layout": "ring", "bore": 0.8, "length": 3.4}

_GALE_CORVETTE = record({
    "id": "gale-corvette",
    # Its points and its parts' drops (MB-GALE-CORVETTE-12).
    "stats": stats({
        "id": "gale-corvette",
        "name": "Gale Corvette",
        "size": 3.2,
        "coreRadius": 15,
        "coreHealth": 1150,
        "points": 3800,
        "groundSpeed": 1.3,
        "parts": [
            part("engine-left", [-ENGINE_GUN_AT[0], ENGINE_GUN_AT[1]], 10, 640),
            part("engine-right", ENGINE_GUN_AT, 10, 640),
            part("bow-gun", [0, -52], 10, 720),
        ],
    }),
    # Where it stops and how it moves in place (MB-GALE-CORVETTE-06): small and fast, wide quick
    # sways.
    "stopFraction": 0.74,
    "sway": {"amplitude": 75, "period": 5.2},
    "bob": {"amplitude": 7, "period": 2.6},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-GALE-CORVETTE-03).
    "mounts": [
        gun_mount(
            "engine-left",
            "engine-left",
            [-ENGINE_GUN_AT[0], ENGINE_GUN_AT[1]],
            ENGINE_GUN_H,
            ENGINE_GUN,
        ),
        gun_mount("engine-right", "engine-right", ENGINE_GUN_AT, ENGINE_GUN_H, ENGINE_GUN),
        gun_mount("bow-gun", "bow-gun", BOW_GUN_AT, GONDOLA_TOP + 0.5, BOW_GUN),
        gun_mount("dorsal", "core", DORSAL_AT, DORSAL_H, DORSAL_GUN),
        gun_mount("stern-rotor", "core", ROTOR_AT, ROTOR_H, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-GALE-CORVETTE-08): chasing aimed
    # fire (the bow gun's bursts, the engine guns' aimed pairs, the dorsal turret's aimed shots and
    # spreads); turned round, straight fans and the stern rotor's rings of 10.
    "stages": stages(
        [
            volley.aimed("engine-left", 2.0, 2, 6, RED, 0.8),
            volley.aimed("engine-right", 2.0, 2, 6, RED, 1.8),
            volley.burst("bow-gun", 2.4, 3, 0.12, ORANGE, 1.3),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, BLUE, 1.5)],
            [volley.aimed("core", 2.4, 3, 8, BLUE, 1)],
            [volley.fan("core", 2.4, 5, 12, ORANGE, 0.8)],
            [
                volley.ring("core", 1.5, 10, 9, BLUE, 0.4),
                volley.aimed("core", 2.6, 2, 6, RED, 1.2),
            ],
        ],
    ),
})

# Where the batteries stand (MB-GALE-CORVETTE-10): on the horizontal stern fins, under their
# fairings; their pods' base (the fin's top) and top.
BATTERY_AT = [16, 40]
BATTERY_POD = [FIN_TOP, FIN_TOP + 2.6]
# The fairings over the stern fins (the right one; mirrored), from the envelope's side out.
FAIRING = [[7, 30], [21, 33.5], [25, 37], [25, 46], [7, 47.5]]  # type: list[list[float]]
FAIRING_TOP = FIN_TOP + 4.5

# Its transformation (BOSS-46, MB-GALE-CORVETTE-10): once both engine guns are gone it turns round
# to bring its stern to bear, the fairings over its stern fins burst off and a battery unfolds on
# each fin. The hatch over its stern rotor bursts as the rotor comes into use, in its last stage
# (BOSS-58).
GALE_CORVETTE = with_weapons(
    merge(
        _GALE_CORVETTE,
        {"transformParts": [["engine-left", "engine-right"]], "turns": [math.pi]},
    ),
    [
        hidden_weapon(
            "battery-left",
            "battery",
            [-BATTERY_AT[0], BATTERY_AT[1]],
            8,
            580,
            1,
            "orange",
            1.2,
            BATTERY_POD,
        ),
        hidden_weapon(
            "battery-right", "battery", BATTERY_AT, 8, 580, 1, "orange", 2.0, BATTERY_POD
        ),
    ],
    [
        armour_region("fairings", 1, FAIRING, "wing", [FIN_TOP - 0.6, FAIRING_TOP]),
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
            "stern-rotor",
        ),
    ],
)
