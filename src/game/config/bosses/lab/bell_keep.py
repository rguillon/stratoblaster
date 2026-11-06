# Copyright (c) 2026 Renaud Guillon
"""The Bell Keep, the Lab's L-12 mini boss (specs/bosses/lab/L-12-bell-keep.md).

Lab boss: in the dev viewer only, no level brings it in. A floating castle: a round stone keep on a
chunk of floating rock (the rock showing round its walls from above, chains hanging off its rim),
a crenellated drum tower either side of its front, a square bell tower at its back and a donjon in
its courtyard. It tolls: slow rings of heavy bullets from the bell tower, aimed pairs from the
towers. Once both front towers are gone its two drawbridges lower (they change shape, BOSS-45), its
portcullises rise and a cannon rolls out onto each bridge: heavy aimed fire.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, swing
from game.config.record import concat, merge, record

# MB-BELL-KEEP-01: the floating rock's top, the courtyard's floor (the gates' sills), the curtain
# wall's outer and inner radius and its top (its merlons standing `MERLON` over it).
ROCK_TOP = 4
FLOOR = 6
WALL_OUT = 27
WALL_IN = 23
WALL_TOP = 16
MERLON = 3
# The gatehouse across the front of the curtain (MB-BELL-KEEP-05): its half width, its front face
# and its top. Its two gates either side of a middle pier: `[x0, x1]` each (the right one), as high
# as `GATE_TOP`.
GATE_HALF = 18
GATE_FRONT = -30
GATE_BACK = -21
GATE_TOP = 19
GATE = [3.5, 14.5]
GATE_OPEN = 14
# A drawbridge: as long as this, as thick as `BRIDGE_THICK`; it is drawn lowered (its top level with
# the sill) and rests raised, swung `BRIDGE_SWING` degrees up about its hinge.
BRIDGE_LENGTH = 12
BRIDGE_THICK = 2
BRIDGE_SWING = -90
# The front towers (MB-BELL-KEEP-03): their centres, radius and top (their crenels round it).
TOWER_AT = [25, -14]
TOWER_RADIUS = 7.5
TOWER_TOP = 26
# The bell tower at the back: its centre, half width and top; the bell rotor on its front.
BELFRY_AT = [0, 26]
BELFRY_HALF = 10
BELFRY_TOP = 22
BELL_ROTOR_AT = [0, 19.5]
# The bell frame over its back half: its posts' corners (x, y), its beam's height; the bell hangs
# from it at `BELL_AT` (MB-BELL-KEEP-04).
BELL_FRAME = [6.5, 26, 34]
BELL_BEAM = 34
BELL_AT = [0, 30]
# The donjon in the courtyard (the core): its centre, radius and top; its turret on its front and
# its rotor under its slate spire behind it.
DONJON_AT = [0, 3]
DONJON_RADIUS = 12
DONJON_TOP = 24
KEEP_GUN_AT = [0, -3.5]
ROTOR_AT = [0, 8]
SPIRE_RADIUS = 6

# The guns (BOSS-58): twin barrels on each front tower, ten barrels round the bell rotor, the
# donjon's three-barrelled turret and its fourteen-barrelled rotor (its last spiral).
TOWER_GUN = {"size": 4.6, "barrels": 2, "gap": 1.4, "bore": 1.1, "length": 7}
BELL_ROTOR = {"size": 4.6, "barrels": 10, "layout": "ring", "bore": 1.0, "length": 3.2}
KEEP_GUN = {"size": 4.6, "barrels": 3, "gap": 1.1, "bore": 1.1, "length": 7}
KEEP_ROTOR = {"size": 4.4, "barrels": 14, "layout": "ring", "bore": 0.8, "length": 3.2}

# Its bullets: the bells' heavy, slow tolls, the towers' red shots, the donjon's magenta ones.
TOLL = bullet("orange", 105, 6)
RED = bullet("red", 185)
MAGENTA = bullet("magenta", 175)
SPIRAL = bullet("orange", 165)

_BELL_KEEP = record({
    "id": "bell-keep",
    # Its points and its parts' drops (MB-BELL-KEEP-11).
    "stats": stats({
        "id": "bell-keep",
        "name": "Bell Keep",
        "size": 3.4,
        "coreRadius": 13,
        "coreHealth": 1000,
        "points": 3500,
        "groundSpeed": 0.4,
        "parts": [
            part("tower-left", [-TOWER_AT[0], TOWER_AT[1]], 10, 600),
            part("tower-right", TOWER_AT, 10, 600),
            part("belfry", BELFRY_AT, 11, 760),
        ],
    }),
    # Where it stops and how it moves in place (MB-BELL-KEEP-06): drifting on its rock.
    "stopFraction": 0.72,
    "sway": {"amplitude": 50, "period": 8.5},
    "bob": {"amplitude": 6, "period": 4.2},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-BELL-KEEP-03).
    "mounts": [
        gun_mount("tower-left", "tower-left", [-TOWER_AT[0], TOWER_AT[1]], TOWER_TOP, TOWER_GUN),
        gun_mount("tower-right", "tower-right", TOWER_AT, TOWER_TOP, TOWER_GUN),
        gun_mount("belfry", "belfry", BELL_ROTOR_AT, BELFRY_TOP, BELL_ROTOR),
        gun_mount("keep-gun", "core", KEEP_GUN_AT, DONJON_TOP, KEEP_GUN),
        gun_mount("keep-rotor", "core", ROTOR_AT, DONJON_TOP, KEEP_ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-BELL-KEEP-08): the bell rotor tolls
    # slow rings of 10 heavy bullets, each turned half a step from the last; the towers sweep aimed
    # pairs in turn; the donjon adds an aimed shot, a burst, an aimed spread, then its rotor's
    # spiral of 14.
    "stages": stages(
        [
            volley.ring("belfry", 3.0, 10, 18, TOLL, 1.0),
            volley.aimed("tower-left", 2.2, 2, 6, RED, 1.4),
            volley.aimed("tower-right", 2.2, 2, 6, RED, 2.5),
        ],
        [
            [volley.aimed("core", 3.0, 1, 0, MAGENTA, 1.5)],
            [volley.burst("core", 2.6, 3, 0.15, MAGENTA, 0.8)],
            [volley.aimed("core", 2.6, 3, 10, MAGENTA, 0.8)],
            [
                volley.ring("core", 1.5, 14, 360 / 28, SPIRAL, 0.4),
                volley.aimed("core", 2.4, 3, 8, MAGENTA, 1.2),
            ],
        ],
    ),
})


def bridge_outline() -> list[list[float]]:
    """Return the right drawbridge's outline, lowered (as drawn): from its hinge out to its tip."""
    return [
        [GATE[0], GATE_FRONT],
        [GATE[1], GATE_FRONT],
        [GATE[1], GATE_FRONT - BRIDGE_LENGTH],
        [GATE[0], GATE_FRONT - BRIDGE_LENGTH],
    ]


# MB-BELL-KEEP-05: each drawbridge swings about its hinge (across the boss, at the gate's sill)
# from raised (at rest) to lowered, as drawn; the left one is its mirror image.
BRIDGE_MOTION = swing([0, GATE_FRONT, FLOOR], "across", [BRIDGE_SWING, 0])
BRIDGE_HEIGHTS = [FLOOR - BRIDGE_THICK - 3, FLOOR + 0.5]
# Where the cannons roll out from (in the courtyard, behind the gates) and where they stop, on the
# lowered bridges (MB-BELL-KEEP-10), and their pods' base and top.
CANNON_FROM = [9, -15]
CANNON_AT = [9, -38]
CANNON_POD = [FLOOR, FLOOR + 2.5]

# Its transformation (BOSS-45, MB-BELL-KEEP-10): once both front towers are gone its drawbridges
# lower and a cannon rolls out of each gate onto its bridge. The slate spire over its donjon's
# rotor bursts as the rotor comes into use, in its last stage (BOSS-58).
BELL_KEEP = with_weapons(
    merge(_BELL_KEEP, {"transformParts": [["tower-left", "tower-right"]]}),
    [
        hidden_weapon(
            "cannon-left",
            "cannon",
            [-CANNON_AT[0], CANNON_AT[1]],
            8,
            610,
            1,
            "red",
            1.2,
            CANNON_POD,
            None,
            [-CANNON_FROM[0], CANNON_FROM[1]],
        ),
        hidden_weapon(
            "cannon-right",
            "cannon",
            CANNON_AT,
            8,
            610,
            1,
            "red",
            2.0,
            CANNON_POD,
            None,
            CANNON_FROM,
        ),
    ],
    concat(
        moving_region("bridge", 1, bridge_outline(), BRIDGE_MOTION, None, BRIDGE_HEIGHTS),
        [
            armour_region(
                "spire",
                None,
                [
                    [
                        ROTOR_AT[0] + SPIRE_RADIUS * math.cos(k * math.pi / 4 + math.pi / 8),
                        ROTOR_AT[1] + SPIRE_RADIUS * math.sin(k * math.pi / 4 + math.pi / 8),
                    ]
                    for k in range(8)
                ],
                "ring",
                None,
                False,
                "keep-rotor",
            ),
        ],
    ),
)
