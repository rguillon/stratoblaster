"""Tunables of the elite enemies (P05-R19 to P05-R23), ported from `config/enemies-elite.ts`.

In the style of `enemies.py`: distances in logical pixels, speeds in px/s, times in seconds, angles
in degrees; `...Fraction` heights are fractions of the playfield height from its bottom. Their
moving parts (P05-R13) are given as drawn facing down the screen at rest, from the enemy's centre
(X right, Y up); `aim` is in radians, clockwise on screen from the nose. Muzzles as in `enemies.py`
(x, y, height).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemies import ENEMY_UNIT
from game.config.record import concat, merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

DEG = math.pi / 180

# Hit radius relative to half the model size (GD-21), as for the first kinds.
HITBOX = 0.85


def radius(size: float) -> float:
    """Hit radius of an enemy `size` L across."""
    return (size * ENEMY_UNIT * HITBOX) / 2


def bullet(style: str, speed: float) -> Any:
    """Enemy bullets: colourful glowing balls (GD-43), styles of `enemy_look`."""
    return record({"speed": speed, "radius": 4, "style": style})


def along_aim(point: Any, aim: float, length: float) -> list[float]:
    """The point `length` px from `point` along `aim` (radians clockwise from the nose, down)."""
    return [point[0] - math.sin(aim) * length, point[1] - math.cos(aim) * length]


def aim_from(frm: Any, to: Any) -> float:
    """The aim (radians clockwise from the nose) from `frm` towards `to`."""
    return math.atan2(frm[0] - to[0], frm[1] - to[1])


def around(count: int, r: float, height: float) -> list[list[float]]:
    """`count` points `r` from the centre, evenly all around, the first one ahead of the nose."""
    return [
        [r * math.sin((2 * math.pi * k) / count), -r * math.cos((2 * math.pi * k) / count), height]
        for k in range(count)
    ]


def fold_entries(entries: list[Any]) -> Any:
    """`Object.fromEntries`: an object of the [key, value] pairs in `entries`."""
    result: dict[str, Any] = {}
    for entry in entries:
        result[entry[0]] = entry[1]
    return result


def swing(amplitude_deg: float, period: float, phase: float) -> Any:
    """A joint's swing: `amplitudeDeg` each way, every `period` s, `phase` of a turn later."""
    return record({"amplitudeDeg": amplitude_deg, "period": period, "phase": phase})


# P05-R19: the Hydra's necks: each a joint at the hull's front, its head at the end.
HYDRA_NECKS = [
    record({"side": "left", "pivot": [-8, -5], "head": [-19, -21]}),
    record({"side": "middle", "pivot": [0, -7], "head": [0, -25]}),
    record({"side": "right", "pivot": [8, -5], "head": [19, -21]}),
]
HYDRA_HEAD = record({"radius": 6.5, "health": 50, "eyeAhead": 5, "eyeHeight": 3})


def hydra_heads() -> list[Any]:
    """The Hydra's heads, one per neck."""
    heads: list[Any] = []
    for i, neck in enumerate(HYDRA_NECKS):
        pivot = neck["pivot"]
        head = neck["head"]
        aim = aim_from(pivot, head)
        eye = along_aim(head, aim, HYDRA_HEAD.eyeAhead)
        heads.append(
            record(
                {
                    "id": "head-" + neck["side"],
                    "joint": "neck-" + neck["side"],
                    "pivot": pivot,
                    "head": head,
                    "aim": aim,
                    # Its eye, where its bullets leave from.
                    "muzzle": [eye[0], eye[1], HYDRA_HEAD.eyeHeight],
                    # The necks sway out of step.
                    "phase": i / len(HYDRA_NECKS),
                }
            )
        )
    return heads


HYDRA_HEADS = hydra_heads()

# P05-R21: the Scissor's arms: hinged at the shoulders, 25 degrees out from straight down at rest.
SCISSOR_ARM = record({"length": 30, "spread": 25, "partAt": 16, "height": 2})


def scissor_arms() -> list[Any]:
    """The Scissor's two arms, left then right."""
    arms: list[Any] = []
    for s in [-1, 1]:
        pivot = [s * 6, 2]
        # Right arm (s = 1): pointing down and to the right, anticlockwise from the nose.
        aim = -s * SCISSOR_ARM.spread * DEG
        centre = along_aim(pivot, aim, SCISSOR_ARM.partAt)
        tip = along_aim(pivot, aim, SCISSOR_ARM.length)
        arms.append(
            record(
                {
                    "id": "arm-left" if s < 0 else "arm-right",
                    "joint": "shoulder-left" if s < 0 else "shoulder-right",
                    "pivot": pivot,
                    "centre": centre,
                    "aim": aim,
                    # Its emitter at the tip, where its laser leaves from.
                    "muzzle": [tip[0], tip[1], SCISSOR_ARM.height],
                    # Its swing turns it inward first (clockwise for the right arm).
                    "phase": 0.5 if s < 0 else 0,
                }
            )
        )
    return arms


SCISSOR_ARMS = scissor_arms()

# P05-R22: the Juggernaut's shoulder cannons and front plates.
JUGGERNAUT_CANNONS = [
    record(
        {
            "id": "cannon-left" if s < 0 else "cannon-right",
            "joint": "shoulder-left" if s < 0 else "shoulder-right",
            "pivot": [s * 22, 3],
            "centre": [s * 28, -3],
            # The tip of its barrel: its bursts leave from there, along it.
            "muzzle": [s * 28, -16, 3],
            "phase": 0.5 if s < 0 else 0,
        }
    )
    for s in [-1, 1]
]
JUGGERNAUT_PLATES = [
    record({"id": "plate-left" if s < 0 else "plate-right", "x": s * 10, "y": -17}) for s in [-1, 1]
]

# P05-R20: the Orbiter's drones, evenly around its core.
ORBITER_DRONE = record({"orbit": 15.5, "radius": 5.5, "health": 40, "muzzleOut": 4.5, "height": 2})


def orbiter_drones() -> list[Any]:
    """The Orbiter's three drones, evenly around its core."""
    drones: list[Any] = []
    for i in range(3):
        a = (2 * math.pi * i) / 3
        sx = math.sin(a)
        sy = math.cos(a)
        out = ORBITER_DRONE.orbit + ORBITER_DRONE.muzzleOut
        drones.append(
            record(
                {
                    "id": "drone-" + str(i),
                    "centre": [ORBITER_DRONE.orbit * sx, ORBITER_DRONE.orbit * sy],
                    # It faces out from the core.
                    "aim": a - math.pi,
                    "muzzle": [out * sx, out * sy, ORBITER_DRONE.height],
                    # The drones fire in turn, not all at once.
                    "firstShot": 1 + (2 * i) / 3,
                }
            )
        )
    return drones


ORBITER_DRONES = orbiter_drones()

ELITE_CONFIG = record(
    {
        "hydra": {
            "stats": {"model": "hydra", "radius": 17, "health": 220, "points": 700},
            "size": 1.6,
            "entrySpeed": 75,
            # It stops in the upper third.
            "stopFraction": 0.74,
            "stay": 7,
            "exitSpeed": 95,
            # One head fires every `headFireInterval`, in turn; the first after `firstShot`.
            "headFireInterval": 0.5,
            "firstShot": 0.4,
            "bullet": bullet("green", 200),
            "heads": HYDRA_HEADS,
            "design": {
                "joints": fold_entries(
                    [
                        [
                            h["joint"],
                            {
                                "x": h["pivot"][0],
                                "y": h["pivot"][1],
                                "swing": swing(16, 2.6, h["phase"]),
                            },
                        ]
                        for h in HYDRA_HEADS
                    ]
                ),
                "parts": [
                    {
                        "id": h["id"],
                        "x": h["head"][0],
                        "y": h["head"][1],
                        "radius": HYDRA_HEAD.radius,
                        "health": HYDRA_HEAD.health,
                        "joint": h["joint"],
                        "aim": h["aim"],
                    }
                    for h in HYDRA_HEADS
                ],
            },
            "xRange": [0.3, 0.7],
        },
        "orbiter": {
            "stats": {"model": "orbiter", "radius": 12, "health": 160, "points": 650},
            "size": 1.1,
            # Radius of its spherical core.
            "coreRadius": 12,
            "entrySpeed": 120,
            # It stops at a random height between these (the upper half).
            "stopRange": [0.6, 0.78],
            "stay": 8,
            "exitSpeed": 140,
            # How fast the drones orbit, degrees per second, clockwise on screen.
            "spin": 100,
            "ringInterval": 3,
            "firstRing": 0.8,
            "ringCount": 12,
            "ringBullet": bullet("orange", 150),
            # Its equator: each bullet of a ring leaves from the point facing its way.
            "ringMuzzles": around(12, 12.5, 0),
            "droneFireInterval": 2,
            "droneBullet": bullet("orange", 200),
            "drones": ORBITER_DRONES,
            "design": {
                "parts": [
                    {
                        "id": d["id"],
                        "x": d["centre"][0],
                        "y": d["centre"][1],
                        "radius": ORBITER_DRONE.radius,
                        "health": ORBITER_DRONE.health,
                        "orbits": True,
                        "aim": d["aim"],
                    }
                    for d in ORBITER_DRONES
                ],
            },
            "xRange": [0.25, 0.75],
        },
        "scissor": {
            "stats": {"model": "scissor", "radius": 14, "health": 240, "points": 800},
            "size": 1.8,
            "entrySpeed": 160,
            # It slows down over this distance before its stop point.
            "brakeDistance": 60,
            "stopFraction": 0.8,
            "exitSpeed": 190,
            # Each arm's laser: 1 s of warning line, then 2 s of beam while the arms close.
            "laser": {"warningSeconds": 1, "firingSeconds": 2, "width": 9, "style": "lancer"},
            # How far each arm swings inward while its laser fires.
            "sweep": 15,
            "arms": SCISSOR_ARMS,
            "design": {
                "joints": fold_entries(
                    [
                        [
                            a["joint"],
                            # A quarter of a period is the firing time: the arm closes by `sweep`
                            # (P05-R21).
                            {
                                "x": a["pivot"][0],
                                "y": a["pivot"][1],
                                "swing": swing(15, 8, a["phase"]),
                            },
                        ]
                        for a in SCISSOR_ARMS
                    ]
                ),
                "parts": [
                    {
                        "id": a["id"],
                        "x": a["centre"][0],
                        "y": a["centre"][1],
                        "radius": 7,
                        "health": 70,
                        "joint": a["joint"],
                        "aim": a["aim"],
                    }
                    for a in SCISSOR_ARMS
                ],
            },
            "xRange": [0.25, 0.75],
        },
        "juggernaut": {
            "stats": {"model": "juggernaut", "radius": 20, "health": 320, "points": 1000},
            "size": 2,
            "entrySpeed": 55,
            "stopFraction": 0.74,
            "drift": 60,
            # Seconds for one left-right drift.
            "driftPeriod": 5,
            "stay": 10,
            "exitSpeed": 80,
            "fireInterval": 2.5,
            "firstShot": 1.2,
            "spreadCount": 7,
            "spreadSpacing": 9,
            "bullet": bullet("blue", 185),
            # The twin cannon on its back turret.
            "muzzles": [
                [-3, -9, 7],
                [3, -9, 7],
            ],
            # Each shoulder cannon fires a burst of `burstCount` along its barrel every interval.
            "cannonInterval": 1.6,
            "firstBurst": 0.8,
            "burstCount": 3,
            "burstGap": 0.12,
            "cannonBullet": bullet("blue", 210),
            "cannons": JUGGERNAUT_CANNONS,
            "plates": JUGGERNAUT_PLATES,
            "design": {
                "joints": fold_entries(
                    [
                        [
                            c["joint"],
                            {
                                "x": c["pivot"][0],
                                "y": c["pivot"][1],
                                "swing": swing(20, 2.4, c["phase"]),
                            },
                        ]
                        for c in JUGGERNAUT_CANNONS
                    ]
                ),
                # While a plate stands, the core cannot be hit (P05-R22).
                "parts": concat(
                    [
                        {
                            "id": c["id"],
                            "x": c["centre"][0],
                            "y": c["centre"][1],
                            "radius": 7,
                            "health": 60,
                            "joint": c["joint"],
                        }
                        for c in JUGGERNAUT_CANNONS
                    ],
                    [
                        merge(p, {"radius": 9, "health": 120, "shields": True})
                        for p in JUGGERNAUT_PLATES
                    ],
                ),
            },
            "xRange": [0.3, 0.7],
        },
        "hive": {
            "stats": {"model": "hive", "radius": radius(2) * 0.8, "health": 420, "points": 900},
            "size": 2,
            "speed": 28,
            # How fast its launch ring turns, degrees per second.
            "ringSpin": 45,
            # A Wasp from the ring every `launchInterval`, the first after `firstLaunch`.
            "launchInterval": 4,
            "firstLaunch": 1.5,
            # The ring's launch hatch, on the turning ring: Wasps come out of it.
            "port": [0, 14, 9],
            # A launched Wasp flies this far down from the hatch before its pause.
            "launchDrop": 55,
            "ringInterval": 3,
            "firstRing": 1,
            "ringCount": 12,
            "ringBullet": bullet("orange", 150),
            # Twelve vents around its rim: each bullet of a ring leaves from the one facing its way.
            "ringMuzzles": around(12, 32, 1),
            # It stops launching and firing below this height, too close to the player.
            "lastFraction": 0.3,
            "design": {"parts": []},
            "xRange": [0.3, 0.7],
        },
    }
)
