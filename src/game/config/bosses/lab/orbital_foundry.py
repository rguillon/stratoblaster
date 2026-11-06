# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-6 final boss, the Orbital Foundry (specs/bosses/lab/L-6-orbital-foundry.md).

An industrial space station seen from above: an armoured reactor sphere in the middle, a fixed
inner ring of gantries and crucibles round it, and an outer track ring turning round them both,
carrying three rotor carriages (BOSS-34). The rotors riding the turning ring paint spirals, the
crucibles lob molten shells that burst into rings (FB-ORBITAL-FOUNDRY-08). Offsets in px from the
boss's centre, X right and Y up (its nose points down, at -Y); angles round the rings in degrees
from its nose, positive towards its right (+X). Lab boss: in the dev viewer only.
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, bursting, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


DEG = math.pi / 180

# FB-ORBITAL-FOUNDRY-01: the reactor sphere (its centre's height and its radius), the inner ring
# (fixed: its centre line's radius, its half width and its deck's height) and the outer ring
# (turning: likewise).
SPHERE_CENTRE = 6
SPHERE_RADIUS = 19
INNER_RADIUS = 40
INNER_HALF = 7
INNER_DECK = 8
OUTER_RADIUS = 66
OUTER_HALF = 4.5
OUTER_TOP = 7


def ring_point(angle: float, radius: float) -> list[float]:
    """Return the point `radius` px from the centre, `angle` degrees round from the nose."""
    a = angle * DEG
    return [radius * math.sin(a), -radius * math.cos(a)]


def arc_outline(angles: list[Any], radii: list[Any]) -> list[list[float]]:
    """Return the outline of the ring's stretch between `angles`, from `radii[0]` to `radii[1]`."""
    steps = 4
    span = [angles[0] + (angles[1] - angles[0]) * k / steps for k in range(steps + 1)]
    result: list[list[float]] = [ring_point(a, radii[1]) for a in span]
    result.extend([ring_point(span[steps - k], radii[0]) for k in range(steps + 1)])
    return result


def fpart(part_id: str, at: list[Any], radius: float, health: float, orbits: bool = False) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6, "orbits": orbits})


ORANGE = bullet("orange", 175)
RED = bullet("red", 185)
MAGENTA = bullet("magenta", 170)
# The crucibles' molten shells: big and slow, bursting into a ring of eight (FB-ORBITAL-FOUNDRY-08).
MOLTEN = bursting("orange", 100, 8, [1.2, 8, bullet("orange", 155)])

# Where its parts stand (FB-ORBITAL-FOUNDRY-03): three rotor carriages on the outer ring, 120
# degrees apart, the first at the nose at rest; a crucible either side of the inner ring.
ROTOR_ANGLES = [0, 120, 240]
CRUCIBLE_ANGLE = 90
# The carriages' rotors: six barrels round a hub, one per bullet of their rings.
ROTOR = {"size": 4.5, "barrels": 6, "layout": "ring", "bore": 1, "length": 4.5}
ROTOR_HEIGHT = 12.5
# The crucibles: squat pots on the inner ring, a mortar on a turntable sunk in each one's molten
# mouth, lobbing its shells.
CRUCIBLE_TOP = 16
CRUCIBLE_MORTAR = {
    "size": 6,
    "barrels": 1,
    "bore": 3.4,
    "length": 4.5,
    "style": "mortar",
    "axis": 0.8,
}
# The core's guns on the reactor sphere: the turret on its front (its aimed shots, fans and
# bursts) and the rotor on its crown (its last ring), under a hatch until then.
REACTOR_GUN_AT = [0, -10]
REACTOR_GUN_HEIGHT = 22.5
REACTOR_ROTOR_AT = [0, 4]
REACTOR_ROTOR_HEIGHT = 24.2
REACTOR_GUN = {"size": 5, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 7}
REACTOR_ROTOR = {"size": 4.6, "barrels": 14, "layout": "ring", "bore": 0.7, "length": 3.2}

_ROTOR_SPOTS = [ring_point(a, OUTER_RADIUS) for a in ROTOR_ANGLES]
_CRUCIBLE_LEFT = ring_point(-CRUCIBLE_ANGLE, INNER_RADIUS)
_CRUCIBLE_RIGHT = ring_point(CRUCIBLE_ANGLE, INNER_RADIUS)

# FB-ORBITAL-FOUNDRY-07: five parts, all shielding the core.
_ORBITAL_FOUNDRY = record({
    "id": "orbital-foundry",
    # Its points, its core's drop and its parts' drops (FB-ORBITAL-FOUNDRY-13).
    "stats": stats({
        "id": "orbital-foundry",
        "name": "Orbital Foundry",
        "size": 4.6,
        "coreRadius": 20,
        "coreHealth": 1800,
        "points": 8000,
        "groundSpeed": 0.3,
        "coreDrop": 1,
        "parts": concat(
            [
                fpart("crucible-left", _CRUCIBLE_LEFT, 12, 900),
                fpart("crucible-right", _CRUCIBLE_RIGHT, 12, 900),
            ],
            [
                fpart("rotor-" + str(k + 1), _ROTOR_SPOTS[k], 11, 760, True)
                for k in range(len(ROTOR_ANGLES))
            ],
        ),
    }),
    # Where it stops and how it moves in place (FB-ORBITAL-FOUNDRY-06): a heavy, slow drift.
    "stopFraction": 0.72,
    "sway": {"amplitude": 30, "period": 11},
    "bob": {"amplitude": 5, "period": 5},
    # Its outer ring turns, the carriages with it (BOSS-34).
    "spinRate": 0.35,
    "guns": {},
    # Its gun mounts (BOSS-58, FB-ORBITAL-FOUNDRY-03): a six-barrelled rotor on each carriage, a
    # mortar in each crucible's mouth, and the core's on the reactor sphere: the turret on its front
    # and the rotor on its crown.
    "mounts": concat(
        [
            gun_mount(
                "rotor-" + str(k + 1),
                "rotor-" + str(k + 1),
                _ROTOR_SPOTS[k],
                ROTOR_HEIGHT,
                merge(ROTOR, {"restDeg": ROTOR_ANGLES[k]}),
            )
            for k in range(len(ROTOR_ANGLES))
        ],
        [
            gun_mount(
                "crucible-left", "crucible-left", _CRUCIBLE_LEFT, CRUCIBLE_TOP, CRUCIBLE_MORTAR
            ),
            gun_mount(
                "crucible-right", "crucible-right", _CRUCIBLE_RIGHT, CRUCIBLE_TOP, CRUCIBLE_MORTAR
            ),
            gun_mount("reactor-gun", "core", REACTOR_GUN_AT, REACTOR_GUN_HEIGHT, REACTOR_GUN),
            gun_mount(
                "reactor-rotor", "core", REACTOR_ROTOR_AT, REACTOR_ROTOR_HEIGHT, REACTOR_ROTOR
            ),
        ],
    ),
    # Its parts' volleys, then the core's pattern per stage (FB-ORBITAL-FOUNDRY-08): the carriages'
    # rotors fire rings in turn, each turned a little more than the last, the ring's turn sweeping
    # them round (spirals); the crucibles lob molten shells at the player in turn; the reactor's
    # turret adds a new pattern at every stage (its fans 12 degrees apart, BOSS-58) and its rotor
    # the last stage's ring.
    "stages": stages(
        [
            volley.ring("rotor-1", 2.2, 6, 13, MAGENTA, 0.6),
            volley.ring("rotor-2", 2.2, 6, 13, MAGENTA, 1.35),
            volley.ring("rotor-3", 2.2, 6, 13, MAGENTA, 2.1),
            volley.aimed("crucible-left", 3.4, 1, 0, MOLTEN, 1.8),
            volley.aimed("crucible-right", 3.4, 1, 0, MOLTEN, 3.5),
        ],
        [
            [volley.aimed("core", 2.6, 3, 10, RED, 1)],
            [volley.fan("core", 2.6, 5, 12, RED, 0.8)],
            [volley.burst("core", 2.2, 4, 0.13, RED, 0.6)],
            [
                volley.fan("core", 2.4, 7, 10, RED, 0.6),
                volley.aimed("core", 3, 1, 0, ORANGE, 1.4),
            ],
            [
                volley.burst("core", 2, 5, 0.12, RED, 0.6),
                volley.fan("core", 2.8, 5, 12, ORANGE, 1.6),
            ],
            [
                volley.ring("core", 1.3, 14, 9, ORANGE, 0.4),
                volley.aimed("core", 2.4, 3, 10, RED, 1),
            ],
        ],
    ),
})

# Where its hidden weapons stand on the inner ring's deck (FB-ORBITAL-FOUNDRY-10,
# FB-ORBITAL-FOUNDRY-11): the sweepers either side of the nose, the cannons either side of the
# back, the hangar on the centre line behind.
SWEEPER_ANGLE = 45
CANNON_ANGLE = 135
# The fairings over them (the right ones; the left ones mirror them): armoured housings on the
# inner ring, the sweepers' shed first, the cannons' and the hangar's second.
FAIRING_RADII = [INNER_RADIUS - INNER_HALF - 1, INNER_RADIUS + INNER_HALF + 1]
FAIRING_HEIGHTS = [INNER_DECK, INNER_DECK + 5]
HANGAR_ARC = [166, 194]
# The hatch over the reactor's rotor: an octagon round its pivot on the sphere's crown.
HATCH = [
    [
        REACTOR_ROTOR_AT[0] + 7 * math.cos(k * math.pi / 4),
        REACTOR_ROTOR_AT[1] + 7 * math.sin(k * math.pi / 4),
    ]
    for k in range(8)
]

# Its transformations (FB-ORBITAL-FOUNDRY-05, FB-ORBITAL-FOUNDRY-10, FB-ORBITAL-FOUNDRY-11): once
# both crucibles are gone the front fairings of the inner ring burst off for a pair of sweepers;
# once the three carriages are gone its rear fairings burst off for a pair of cannons and a hangar
# on its centre line. The hatch over the reactor's rotor bursts as the rotor comes into use.
ORBITAL_FOUNDRY = with_weapons(
    merge(
        _ORBITAL_FOUNDRY,
        {
            "transformParts": [
                ["crucible-left", "crucible-right"],
                ["rotor-1", "rotor-2", "rotor-3"],
            ]
        },
    ),
    [
        hidden_weapon(
            "sweeper-left",
            "sweeper",
            ring_point(-SWEEPER_ANGLE, INNER_RADIUS),
            7,
            720,
            1,
            "orange",
            1.2,
            [INNER_DECK, INNER_DECK + 3],
        ),
        hidden_weapon(
            "sweeper-right",
            "sweeper",
            ring_point(SWEEPER_ANGLE, INNER_RADIUS),
            7,
            720,
            1,
            "orange",
            4.2,
            [INNER_DECK, INNER_DECK + 3],
        ),
        hidden_weapon(
            "cannon-left",
            "cannon",
            ring_point(-CANNON_ANGLE, INNER_RADIUS),
            8.5,
            900,
            2,
            "red",
            1.4,
            [INNER_DECK, INNER_DECK + 3.5],
        ),
        hidden_weapon(
            "cannon-right",
            "cannon",
            ring_point(CANNON_ANGLE, INNER_RADIUS),
            8.5,
            900,
            2,
            "red",
            2.6,
            [INNER_DECK, INNER_DECK + 3.5],
        ),
        hidden_weapon(
            "hangar",
            "hangar",
            [0, INNER_RADIUS],
            9,
            900,
            2,
            "orange",
            2.2,
            [INNER_DECK, INNER_DECK + 3.5],
        ),
    ],
    [
        armour_region(
            "front-fairings",
            1,
            arc_outline([SWEEPER_ANGLE - 15, SWEEPER_ANGLE + 15], FAIRING_RADII),
            "shell",
            FAIRING_HEIGHTS,
        ),
        armour_region(
            "rear-fairings",
            2,
            arc_outline([CANNON_ANGLE - 16, CANNON_ANGLE + 16], FAIRING_RADII),
            "shell",
            FAIRING_HEIGHTS,
        ),
        armour_region(
            "hangar-fairing",
            2,
            arc_outline(HANGAR_ARC, FAIRING_RADII),
            "shell",
            FAIRING_HEIGHTS,
            False,
        ),
        armour_region("rotor-hatch", None, HATCH, "ring", None, False, "reactor-rotor"),
    ],
)
