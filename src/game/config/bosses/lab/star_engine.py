# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-10 final boss, the Star Engine (specs/bosses/lab/L-10-star-engine.md).

A five-pointed star of a reactor: a spiky pentagonal core, five long armoured thruster arms
radiating from it, each tipped by an emitter, and a containment ring round the core. Lab boss: in
the dev viewer only (no level brings it in). Offsets in px from the boss's centre, X right and Y up
(its nose points down, at -Y); angles round the star in degrees from its nose, positive towards its
right (+X).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


DEG = math.pi / 180

# FB-STAR-ENGINE-01: the five arms' headings (the nose arm, the side arms, the back arms), the
# pentagonal core's radius (to its corners, between the arms) and its deck's height, the arms'
# reach (their emitters' centres), their width at the root and at the tip and their top's height.
ARM_ANGLES = [0, 72, -72, 144, -144]
CORE_RADIUS = 27
DECK_RADIUS = 44
DECK_TOP = 7
ARM_REACH = 63
ARM_ROOT = 9
ARM_TIP = 5.5
ARM_TOP = 12
# The containment ring round the core (FB-STAR-ENGINE-02): its radius, its tube's girth and its
# axis's height, over the arms.
RING_RADIUS = 43
RING_GIRTH = 2.4
RING_AXIS = 15.5
# The reactor dome on the core: its crown's height (the heart rotor stands on it).
DOME_TOP = 26
# The emitters at the arms' tips: their rotors' height.
TIP_ROTOR_HEIGHT = 19
# The core's star turret on the reactor's front, before the dome.
STAR_GUN_AT = [0, -17]
STAR_GUN_HEIGHT = 15


def star_point(angle: float, radius: float) -> list[float]:
    """Return the point `radius` px from the centre, `angle` degrees round from the nose."""
    a = angle * DEG
    return [radius * math.sin(a), -radius * math.cos(a)]


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


RED = bullet("red", 175)
MAGENTA = bullet("magenta", 165)
ORANGE = bullet("orange", 195)

# The arms' parts, in the order of `ARM_ANGLES` (FB-STAR-ENGINE-03).
TIP_IDS = ["tip-nose", "tip-right", "tip-left", "tip-back-right", "tip-back-left"]
TIP_HEALTH = [1900, 1600, 1600, 1700, 1700]
# Each emitter's rotor: five barrels, its turning rings (a pentagram from every arm).
TIP_ROTOR = {"size": 4.6, "barrels": 5, "layout": "ring", "bore": 1.1, "length": 5}
# The heart rotor on the reactor dome: fifteen barrels, the core's spirals.
HEART_ROTOR = {"size": 6, "barrels": 15, "layout": "ring", "bore": 0.85, "length": 5}
# The star turret: five barrels side by side, its aimed shots, bursts and fans.
STAR_GUN = {"size": 5, "barrels": 5, "gap": 1, "bore": 0.9, "length": 7}
# Each emitter's rings: every so often, turning one way or the other in turn round the star.
TIP_EVERY = 1.9
TIP_TURN = [14, -14, -14, 14, 14]
TIP_FIRST = [0.6, 1.0, 1.4, 1.8, 2.2]

_TIPS = [star_point(ARM_ANGLES[k], ARM_REACH) for k in range(5)]

# FB-STAR-ENGINE-07: five parts, the arms' emitters, all shielding the core.
_STAR_ENGINE = record({
    "id": "star-engine",
    # Its points, its core's drop and its parts' drops (FB-STAR-ENGINE-13).
    "stats": stats({
        "id": "star-engine",
        "name": "Star Engine",
        "size": 4.5,
        "coreRadius": 24,
        "coreHealth": 5700,
        "points": 16000,
        "groundSpeed": 0.3,
        "coreDrop": 1,
        "parts": [fpart(TIP_IDS[k], _TIPS[k], 12, TIP_HEALTH[k]) for k in range(5)],
    }),
    # Where it stops and how it moves in place (FB-STAR-ENGINE-06).
    "stopFraction": 0.72,
    "sway": {"amplitude": 26, "period": 12},
    "bob": {"amplitude": 5, "period": 5.5},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-STAR-ENGINE-03): a five-barrelled rotor on each emitter, and the
    # core's: the fifteen-barrelled heart rotor on the reactor dome and the star turret before it.
    "mounts": concat(
        [
            gun_mount(TIP_IDS[k], TIP_IDS[k], _TIPS[k], TIP_ROTOR_HEIGHT, TIP_ROTOR)
            for k in range(5)
        ],
        [
            gun_mount("heart", "core", [0, 0], DOME_TOP, HEART_ROTOR),
            gun_mount("star-gun", "core", STAR_GUN_AT, STAR_GUN_HEIGHT, STAR_GUN),
        ],
    ),
    # Its parts' volleys, then the core's pattern per stage (FB-STAR-ENGINE-08): every emitter
    # spins its ring of five, in turn round the star, one way or the other; the heart rotor's
    # rings of fifteen turn by fifths of a barrel's spacing (pentagram spirals), faster at every
    # stage, and the star turret adds aimed shots, bursts and fans (12° apart, BOSS-58).
    "stages": stages(
        [
            volley.ring(TIP_IDS[k], TIP_EVERY, 5, TIP_TURN[k], MAGENTA, TIP_FIRST[k])
            for k in range(5)
        ],
        [
            [
                volley.ring("core", 2.4, 15, 12, ORANGE, 1),
                volley.aimed("core", 3, 1, 0, RED, 1.6),
            ],
            [
                volley.ring("core", 2, 15, -12, ORANGE, 0.8),
                volley.aimed("core", 2.6, 3, 12, RED, 1.2),
            ],
            [
                volley.ring("core", 1.6, 15, 4.8, ORANGE, 0.6),
                volley.burst("core", 2.4, 4, 0.13, RED, 1),
            ],
            [
                volley.ring("core", 1.3, 15, -4.8, ORANGE, 0.6),
                volley.fan("core", 2.4, 5, 12, RED, 1),
            ],
            [
                volley.ring("core", 1.1, 15, 9.6, ORANGE, 0.5),
                volley.burst("core", 2.2, 5, 0.12, RED, 1),
            ],
            [
                volley.ring("core", 0.65, 15, 7.2, ORANGE, 0.4),
                volley.fan("core", 2, 5, 12, RED, 1),
            ],
        ],
    ),
})

# Where the hidden weapons stand (FB-STAR-ENGINE-10, FB-STAR-ENGINE-11): the orbs on the core's
# deck between the nose arm and the side arms, the gatlings between the side arms and the back
# arms, the lance on the nose arm, on the centre line.
ORB_AT = star_point(36, 33)
GATLING_AT = star_point(108, 33)
LANCE_AT = [0, -38]


def _sector(angle: float, radii: list[Any], half: float) -> list[list[float]]:
    """Return the outline of the deck's sector `half` degrees either side of `angle`.

    From `radii[0]` out to `radii[1]`, its outer edge in three steps.
    """
    result: list[list[float]] = [
        star_point(angle - half, radii[0]),
        star_point(angle + half, radii[0]),
    ]
    result.extend([star_point(angle + half - 2 * half * k / 3, radii[1]) for k in range(4)])
    return result


# The vanes over the deck's front sectors (shed at the first transformation), the cowls over its
# side sectors and the keel plate along the nose arm (shed at the second), and their heights.
VANE_OUTLINE = _sector(36, [CORE_RADIUS - 1, 37], 15)
COWL_OUTLINE = _sector(108, [CORE_RADIUS - 1, 37], 15)
KEEL_OUTLINE = [[-8, -28], [8, -28], [7, -48], [-7, -48]]
PLATE_HEIGHTS = [DECK_TOP - 0.5, DECK_TOP + 5]
KEEL_HEIGHTS = [ARM_TOP - 0.5, ARM_TOP + 3.5]

# Its transformations (FB-STAR-ENGINE-05): once both side emitters are gone the vanes over the
# deck's front burst off for a pair of orbs; once both back emitters are gone the cowls and the
# keel plate burst off for a pair of gatlings and a lance on the nose arm.
STAR_ENGINE = with_weapons(
    merge(
        _STAR_ENGINE,
        {"transformParts": [["tip-left", "tip-right"], ["tip-back-left", "tip-back-right"]]},
    ),
    [
        hidden_weapon(
            "orb-left", "orb", [-ORB_AT[0], ORB_AT[1]], 9, 1520, 1, "magenta", 1.2, [DECK_TOP, 11]
        ),
        hidden_weapon("orb-right", "orb", ORB_AT, 9, 1520, 1, "magenta", 2.0, [DECK_TOP, 11]),
        hidden_weapon(
            "gatling-left",
            "gatling",
            [-GATLING_AT[0], GATLING_AT[1]],
            8,
            1900,
            2,
            "red",
            1.2,
            [DECK_TOP, 11],
        ),
        hidden_weapon(
            "gatling-right", "gatling", GATLING_AT, 8, 1900, 2, "red", 2.0, [DECK_TOP, 11]
        ),
        hidden_weapon("lance", "lance", LANCE_AT, 8, 1900, 2, "red", 1.6, [ARM_TOP, ARM_TOP + 3]),
    ],
    [
        armour_region("vanes", 1, VANE_OUTLINE, "shell", PLATE_HEIGHTS),
        armour_region("cowls", 2, COWL_OUTLINE, "shell", PLATE_HEIGHTS),
        armour_region("keel", 2, KEEL_OUTLINE, "wing", KEEL_HEIGHTS, False),
    ],
)
