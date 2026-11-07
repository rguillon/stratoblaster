# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-6 mini boss, the Prism Gate (specs/bosses/lab/L-6-prism-gate.md).

A hollow equilateral triangle of heavy metal girders, one point towards the player, a crystal prism
hung on cables in its middle. A big faceted crystal emitter at each corner fires a laser along a
fixed line, so the three beams fence the playfield into lanes, while the prism's turret sweeps its
fans between them and adds a new pattern at every stage (MB-PRISM-GATE-08). Offsets in px from the
boss's centre, X right and Y up (its nose points down, at -Y). Lab boss: in the dev viewer only.
"""

import math

from game.config.bosses.boss_guns import gun_mount, laser_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


DEG = math.pi / 180

# MB-PRISM-GATE-01: the corners' hubs, `GATE_RADIUS` px from the centre, the nose one pointing down
# the screen; the girders between them, from `GIRDER_BOTTOM` to `GIRDER_TOP` high, `GIRDER_WIDTH`
# across; the hubs' tops.
GATE_RADIUS = 48
GIRDER_BOTTOM = 2
GIRDER_TOP = 9
GIRDER_WIDTH = 9
HUB_TOP = 11
NOSE_AT = [0, -GATE_RADIUS]
LEFT_AT = [-GATE_RADIUS * math.sin(120 * DEG), GATE_RADIUS * 0.5]
RIGHT_AT = [GATE_RADIUS * math.sin(120 * DEG), GATE_RADIUS * 0.5]

# The corners' lasers (MB-PRISM-GATE-03): fixed emitters on the hubs, each `LASER_OUT` px out along
# its beam's line; the nose's points straight down, the flanks' `FLANK_TILT` degrees in, so the
# three beams cross below the boss and fence the playfield into lanes.
CORNER_LASER = {"size": 4, "bore": 2, "length": 8}
LASER_OUT = 8
FLANK_TILT = 10


def _laser_spot(corner: list[Any], tilt_deg: float) -> list[float]:
    """Return where a corner's laser stands: `LASER_OUT` px from the hub along its beam's line."""
    a = tilt_deg * DEG
    return [corner[0] - math.sin(a) * LASER_OUT, corner[1] - math.cos(a) * LASER_OUT]


# The prism (MB-PRISM-GATE-02): an upright triangular crystal, `PRISM_RADIUS` round its axis,
# pointing the other way from the gate, hung from `PRISM_BOTTOM` to `PRISM_TOP`, a dark metal crown
# on it up to `CROWN_TOP` carrying the core's guns.
PRISM_RADIUS = 18
PRISM_BOTTOM = 11
PRISM_TOP = 23
CROWN_RADIUS = 10.5
CROWN_TOP = 25.5
# The core's guns on the crown: the prism turret (its fans, aimed spreads and bursts) and the rotor
# behind it (its last ring), under a hatch until then.
TURRET_AT = [0, -5]
ROTOR_AT = [0, 5]
PRISM_GUN = {"size": 4.5, "barrels": 3, "gap": 1.1, "bore": 1, "length": 6.5}
PRISM_ROTOR = {"size": 3.6, "barrels": 12, "layout": "ring", "bore": 0.7, "length": 2.6}

BLUE = bullet("blue", 175)
GREEN = bullet("green", 165)
MAGENTA = bullet("magenta", 185)

_PRISM_GATE = record({
    "id": "prism-gate",
    # Its points and its parts' drops (MB-PRISM-GATE-11).
    "stats": stats({
        "id": "prism-gate",
        "name": "Prism Gate",
        "size": 3.6,
        "coreRadius": 13,
        "coreHealth": 900,
        "points": 3500,
        "groundSpeed": 0.6,
        "parts": [
            part("crystal-left", LEFT_AT, 13, 520),
            part("crystal-right", RIGHT_AT, 13, 520),
            part("crystal-nose", NOSE_AT, 13, 600),
        ],
    }),
    # Where it stops and how it moves in place (MB-PRISM-GATE-06): a slow, stately drift.
    "stopFraction": 0.72,
    "sway": {"amplitude": 45, "period": 10},
    "bob": {"amplitude": 5, "period": 4.5},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-PRISM-GATE-03): a fixed laser emitter on each corner's hub, in
    # front of its crystal, and the core's on the prism's crown: the turret and the rotor (under a
    # hatch until its last stage).
    "mounts": [
        laser_mount(
            "crystal-left",
            "crystal-left",
            _laser_spot(LEFT_AT, -FLANK_TILT),
            HUB_TOP,
            merge(CORNER_LASER, {"restDeg": -FLANK_TILT}),
        ),
        laser_mount(
            "crystal-right",
            "crystal-right",
            _laser_spot(RIGHT_AT, FLANK_TILT),
            HUB_TOP,
            merge(CORNER_LASER, {"restDeg": FLANK_TILT}),
        ),
        laser_mount("crystal-nose", "crystal-nose", _laser_spot(NOSE_AT, 0), HUB_TOP, CORNER_LASER),
        gun_mount("prism-gun", "core", TURRET_AT, CROWN_TOP, PRISM_GUN),
        gun_mount("prism-rotor", "core", ROTOR_AT, CROWN_TOP, PRISM_ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-PRISM-GATE-08): the flanks' beams
    # fire together, a V fencing the player in, the nose's between them, splitting the V; the
    # prism's turret sweeps fans along the gate's lines (12 degrees apart), then aimed spreads and
    # bursts, and its rotor fires the last stage's ring.
    "stages": stages(
        [
            volley.laser("crystal-left", 7, 1.6, 1.5),
            volley.laser("crystal-right", 7, 1.6, 1.5),
            volley.laser("crystal-nose", 6, 1.4, 4.5),
        ],
        [
            [
                volley.fan("core", 3.2, 5, 12, BLUE, 1, -20),
                volley.fan("core", 3.2, 5, 12, BLUE, 2.6, 20),
            ],
            [
                volley.aimed("core", 2.2, 3, 10, MAGENTA, 0.8),
                volley.fan("core", 3, 7, 12, BLUE, 1.6),
            ],
            [
                volley.burst("core", 2, 4, 0.13, MAGENTA, 0.6),
                volley.fan("core", 2.8, 5, 12, BLUE, 1.2, -30),
                volley.fan("core", 2.8, 5, 12, BLUE, 2.6, 30),
            ],
            [
                volley.ring("core", 1.4, 12, 11, GREEN, 0.4),
                volley.aimed("core", 2.4, 1, 0, MAGENTA, 1),
            ],
        ],
    ),
})

# MB-PRISM-GATE-05: the housing over the back girder (the right one; the left one mirrors it), shed
# at its transformation; the racks lie folded under it, on the girder.
HOUSING = [[7.0, GATE_RADIUS * 0.5 - 7], [31.0, GATE_RADIUS * 0.5 - 7], [31.0, 31.0], [7.0, 31.0]]
HOUSING_HEIGHTS = [GIRDER_TOP, GIRDER_TOP + 4.5]
RACK_AT = 19
# The hatch over the prism's rotor: an octagon round its pivot on the crown.
HATCH = [
    [ROTOR_AT[0] + 5.5 * math.cos(k * math.pi / 4), ROTOR_AT[1] + 5.5 * math.sin(k * math.pi / 4)]
    for k in range(8)
]

# Its transformation (MB-PRISM-GATE-10): once both flank crystals are gone the housings on its
# back girder burst off and a pair of missile racks unfold on the girder. The hatch over the
# prism's rotor bursts as the rotor comes into use, in its last stage (BOSS-58).
PRISM_GATE = with_weapons(
    merge(_PRISM_GATE, {"transformParts": [["crystal-left", "crystal-right"]]}),
    [
        hidden_weapon(
            "rack-left",
            "rack",
            [-RACK_AT, GATE_RADIUS * 0.5],
            7,
            480,
            1,
            "blue",
            1.2,
            [GIRDER_TOP, GIRDER_TOP + 3],
        ),
        hidden_weapon(
            "rack-right",
            "rack",
            [RACK_AT, GATE_RADIUS * 0.5],
            7,
            480,
            1,
            "blue",
            2.0,
            [GIRDER_TOP, GIRDER_TOP + 3],
        ),
    ],
    [
        armour_region("housings", 1, HOUSING, "shell", HOUSING_HEIGHTS),
        armour_region("rotor-hatch", None, HATCH, "ring", None, False, "prism-rotor"),
    ],
)
