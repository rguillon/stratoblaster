# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-19 final boss, the Tiltrotor Behemoth (specs/bosses/lab/L-19-tiltrotor-behemoth.md).

Lab boss: in the dev viewer only (no level brings it in). A gigantic tiltrotor seen from above: a
boxy fuselage with a glazed nose and a rear ramp, a wide high wing across its back, and at each
wingtip a huge rotor nacelle standing up in a forked cradle, its three-bladed rotor turning over
it. It fights as a gunship hovering: aimed pairs from its wing guns, bursts from its tail guns,
sweeping fans from its nose gun.

At its first transformation each rotor nacelle **morphs into a turbine cannon** (its view rig):
the rotor spins down, the blades fold back along the nacelle, the nacelle tilts forward in its
cradle, then slides in along the wing's leading edge onto a sponson by the fuselage, its spinner
opening in petals as a heavy cannon turret rises out of it (a `cannon` pair, sliding out of the
wingtips: `out_of`). At its second the outer **wing halves swing round on their roots and stow
along the fuselage** (moving pieces, BOSS-45) like a carrier aircraft's, their leading-edge slats
flipping up into walls, and the plane is a compact flying gun tower: a `sweeper` rides out on each
stowed half and the spine fairing bursts off a `mortar` on the centre line.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import move_point, moving_region, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# FB-TILTROTOR-BEHEMOTH-01: the fuselage, from its nose to its roof's end, its half width, its
# belly and roof; the rear ramp behind it, down to `RAMP_END`.
NOSE = -84
TAIL = 58
RAMP_END = 72
HALF = 15
BELLY = 2
ROOF = 20
# The wing (FB-TILTROTOR-BEHEMOTH-02): its chord `[y0, y1]`; the centre section on the roof, out
# to `CENTRE_X`, `[low, top]`; the outer halves out to `WING_TIP_X`, on top of it (`OUTER_H`).
CHORD = [-14, 8]
CENTRE_X = 30
CENTRE_H = [ROOF, 24]
WING_TIP_X = 72
OUTER_H = [24.2, 27.4]
# The forked cradle at each wingtip the nacelle stands in: `[x0, x1, y0, y1]`, `[low, top]`.
CRADLE = [70, 86, -9, 5]
CRADLE_H = [16, 29]
# The rotor nacelles (FB-TILTROTOR-BEHEMOTH-05): their pivot in the cradle `[x, y]` (the
# nacelle's root) and its height, their radius and length (standing up from the pivot, or tilted
# forward), and the rotor's blades' reach.
NACELLE_AT = [78, -2]
NACELLE_H = 22
NACELLE_RADIUS = 6
NACELLE_LENGTH = 24
ROTOR_RADIUS = 26

# The outer wing halves (FB-TILTROTOR-BEHEMOTH-11): the right one as drawn (spread), its cradle
# with it; it swings round about its leading root (`WING_PIVOT`) a quarter turn back, to lie
# along the fuselage.
WING = [  # type: list[list[float]]
    [CENTRE_X, CHORD[0]],
    [WING_TIP_X, CHORD[0]],
    [CRADLE[1], CRADLE[2]],
    [CRADLE[1], CRADLE[3]],
    [WING_TIP_X, CHORD[1]],
    [CENTRE_X, CHORD[1]],
]
WING_PIVOT = [CENTRE_X, CHORD[0], OUTER_H[0]]
STOW = 90
WING_SWING = swing(WING_PIVOT, "up", [0, STOW])

GOLD = bullet("orange", 180)
RED = bullet("red", 190)
PURPLE = bullet("purple", 175)


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


def stowed(spot: list[Any]) -> list[float]:
    """Where `spot` of the right outer wing as drawn lies once it has stowed."""
    q = move_point(WING_SWING, STOW, [spot[0], spot[1], 0])
    return [math.floor(q[0] * 10 + 0.5) / 10, math.floor(q[1] * 10 + 0.5) / 10]


# Its guns (BOSS-58, FB-TILTROTOR-BEHEMOTH-03): twin barrels on each wing gun's turret (on the
# outer wings), three on each tail gun's and on the nose gun's, and the core's: a three-barrelled
# dorsal turret ahead of the wing and a rotor behind it, under a hatch until its last stage.
WING_GUN_AT = [44, -3]
WING_GUN_H = OUTER_H[1] + 2.6
WING_GUN = {"size": 5, "barrels": 2, "gap": 3, "bore": 1.1, "length": 8}
TAIL_GUN_AT = [9, 52]
TAIL_GUN = {"size": 4.4, "barrels": 3, "gap": 1.2, "bore": 1, "length": 7}
NOSE_GUN_AT = [0, -70]
NOSE_GUN_H = 19.5
NOSE_GUN = {"size": 5.2, "barrels": 3, "gap": 1.3, "bore": 1.2, "length": 8.5}
DORSAL_AT = [0, -36]
DORSAL_GUN = {"size": 5.6, "barrels": 3, "gap": 1.3, "bore": 1.2, "length": 8.5}
ROTOR_AT = [0, 38]
ROTOR = {"size": 5, "barrels": 14, "layout": "ring", "bore": 0.75, "length": 3.6}
GUN_H = ROOF + 0.5

_TILTROTOR_BEHEMOTH = record({
    "id": "tiltrotor-behemoth",
    # Its points, its core's drop and its parts' drops (FB-TILTROTOR-BEHEMOTH-13).
    "stats": stats({
        "id": "tiltrotor-behemoth",
        "name": "Tiltrotor Behemoth",
        "size": 6,
        "coreRadius": 20,
        "coreHealth": 4700,
        "points": 15000,
        "groundSpeed": 0.6,
        "coreDrop": 1,
        "parts": [
            fpart("wing-left", [-WING_GUN_AT[0], WING_GUN_AT[1]], 9, 1300),
            fpart("wing-right", WING_GUN_AT, 9, 1300),
            fpart("tail-left", [-TAIL_GUN_AT[0], TAIL_GUN_AT[1]], 8, 1250),
            fpart("tail-right", TAIL_GUN_AT, 8, 1250),
            fpart("nose-gun", NOSE_GUN_AT, 10, 1400),
        ],
    }),
    # Where it stops and how it moves in place (FB-TILTROTOR-BEHEMOTH-06): a huge, heavy machine
    # hovering, slow sways.
    "stopFraction": 0.7,
    "sway": {"amplitude": 28, "period": 11},
    "bob": {"amplitude": 5, "period": 4.6},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-TILTROTOR-BEHEMOTH-03).
    "mounts": [
        gun_mount(
            "wing-left", "wing-left", [-WING_GUN_AT[0], WING_GUN_AT[1]], WING_GUN_H, WING_GUN
        ),
        gun_mount("wing-right", "wing-right", WING_GUN_AT, WING_GUN_H, WING_GUN),
        gun_mount("tail-left", "tail-left", [-TAIL_GUN_AT[0], TAIL_GUN_AT[1]], GUN_H, TAIL_GUN),
        gun_mount("tail-right", "tail-right", TAIL_GUN_AT, GUN_H, TAIL_GUN),
        gun_mount("nose-gun", "nose-gun", NOSE_GUN_AT, NOSE_GUN_H, NOSE_GUN),
        gun_mount("dorsal", "core", DORSAL_AT, GUN_H, DORSAL_GUN),
        gun_mount("spine-rotor", "core", ROTOR_AT, GUN_H, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-TILTROTOR-BEHEMOTH-08): the wing
    # guns' aimed pairs, the tail guns' bursts, the nose gun's fans swept straight down; the core
    # adds a new pattern at each stage, ending in the spine rotor's spiral of 14.
    "stages": stages(
        [
            volley.aimed("wing-left", 2.0, 2, 6, RED, 0.8),
            volley.aimed("wing-right", 2.0, 2, 6, RED, 1.8),
            volley.burst("tail-left", 2.6, 3, 0.12, GOLD, 1.2),
            volley.burst("tail-right", 2.6, 3, 0.12, GOLD, 2.4),
            volley.fan("nose-gun", 3, 5, 12, PURPLE, 1.5),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, GOLD, 1.4)],
            [volley.aimed("core", 2.6, 3, 8, GOLD, 1)],
            [volley.burst("core", 2.4, 4, 0.13, RED, 0.8)],
            [
                volley.fan("core", 2.6, 5, 12, PURPLE, 0.6),
                volley.aimed("core", 3, 1, 0, RED, 1.6),
            ],
            [
                volley.fan("core", 2.4, 7, 10, PURPLE, 0.6),
                volley.burst("core", 2.8, 3, 0.13, RED, 1.5),
            ],
            [
                volley.ring("core", 1.4, 14, 9, PURPLE, 0.4),
                volley.aimed("core", 2.8, 3, 8, GOLD, 1.2),
            ],
        ],
    ),
})

# Where the hidden weapons stand. The cannons (FB-TILTROTOR-BEHEMOTH-10): their turret at the front
# of the nacelle docked on a sponson by the fuselage, slid in from the tilted nacelle at the
# wingtip (`CANNON_FROM`); their pod's base and top (the turret's barrels on the nacelle's axis).
CANNON_AT = [26, -50]
CANNON_RADIUS = 10
CANNON_FROM = [NACELLE_AT[0], NACELLE_AT[1] - NACELLE_LENGTH - 3]
CANNON_POD = [16, 19.3]
# The sponsons they dock on: `[x0, x1, y0, y1]`, `[low, top]`.
SPONSON = [HALF - 1, 34, -54, -18]
SPONSON_H = [8, 15.5]
# The sweepers (FB-TILTROTOR-BEHEMOTH-11) ride the stowed wing halves; the mortar stands on the
# centre line behind the wing, under the spine fairing.
SWEEPER_AT = stowed([60, -3])
SWEEPER_POD = [OUTER_H[1], OUTER_H[1] + 3]
MORTAR_AT = [0, 18]
MORTAR_POD = [ROOF, ROOF + 2.5]
FAIRING = [[-7, 10], [7, 10], [7, 27], [0, 29.5], [-7, 27]]  # type: list[list[float]]
FAIRING_TOP = ROOF + 5

# Its transformations: once both wing guns are gone its rotor nacelles morph into turbine cannons
# that slide in onto its sponsons; once both tail guns are gone its outer wing halves stow along
# the fuselage, a sweeper riding each, and the spine fairing bursts off a mortar. The hatch over
# the spine rotor bursts as the rotor comes into use, in its last stage (BOSS-58).
TILTROTOR_BEHEMOTH = with_weapons(
    merge(
        _TILTROTOR_BEHEMOTH,
        {"transformParts": [["wing-left", "wing-right"], ["tail-left", "tail-right"]]},
    ),
    [
        hidden_weapon(
            "cannon-left",
            "cannon",
            [-CANNON_AT[0], CANNON_AT[1]],
            CANNON_RADIUS,
            1600,
            1,
            "orange",
            1.2,
            CANNON_POD,
            None,
            [-CANNON_FROM[0], CANNON_FROM[1]],
        ),
        hidden_weapon(
            "cannon-right",
            "cannon",
            CANNON_AT,
            CANNON_RADIUS,
            1600,
            1,
            "orange",
            2.4,
            CANNON_POD,
            None,
            CANNON_FROM,
        ),
        hidden_weapon(
            "sweeper-left",
            "sweeper",
            [-SWEEPER_AT[0], SWEEPER_AT[1]],
            8,
            1400,
            2,
            "red",
            1.2,
            SWEEPER_POD,
        ),
        hidden_weapon("sweeper-right", "sweeper", SWEEPER_AT, 8, 1400, 2, "red", 4.5, SWEEPER_POD),
        hidden_weapon("mortar", "mortar", MORTAR_AT, 7, 1500, 2, "purple", 1.8, MORTAR_POD),
    ],
    concat(
        moving_region("wing", 2, WING, WING_SWING, None, [OUTER_H[0] - 0.5, 1000]),
        [
            armour_region("spine-fairing", 2, FAIRING, "shell", [ROOF - 0.5, FAIRING_TOP], False),
            armour_region(
                "rotor-hatch",
                None,
                [
                    [
                        ROTOR_AT[0] + 6.4 * math.cos(k * math.pi / 4 + math.pi / 8),
                        ROTOR_AT[1] + 6.4 * math.sin(k * math.pi / 4 + math.pi / 8),
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
