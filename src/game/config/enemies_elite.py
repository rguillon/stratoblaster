# Copyright (c) 2026 Renaud Guillon
"""Tunables of the elite enemies (ENM-06; each kind's file in specs/enemies/).

In the style of `enemies.py`: distances in logical pixels, speeds in px/s, times in seconds, angles
in degrees; `...Fraction` heights are fractions of the playfield height from its bottom. Their
moving parts (ENM-27, ENM-28) are given as drawn facing down the screen at rest, from the enemy's
centre (X right, Y up); `aim` is in radians, clockwise on screen from the nose. Muzzles as in
`enemies.py` (x, y, height).
"""

import math

from game.config.enemies import ENEMY_UNIT
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


DEG = math.pi / 180

# Hit radius relative to half the model size (ENM-11), as for the first kinds.
HITBOX = 0.85


def radius(size: float) -> float:
    """Hit radius of an enemy `size` L across."""
    return (size * ENEMY_UNIT * HITBOX) / 2


def bullet(style: str, speed: float) -> Any:
    """Enemy bullets: colourful glowing balls (ENM-16), styles of `enemy_look`."""
    return record({"speed": speed, "radius": 4, "style": style})


def along_aim(point: Any, aim: float, length: float) -> list[float]:
    """Return the point `length` px from `point` along `aim`.

    `aim` is in radians clockwise from the nose, down.
    """
    return [point[0] - math.sin(aim) * length, point[1] - math.cos(aim) * length]


def aim_from(frm: Any, to: Any) -> float:
    """Return the aim (radians clockwise from the nose) from `frm` towards `to`."""
    return math.atan2(frm[0] - to[0], frm[1] - to[1])


def around(count: int, r: float, height: float) -> list[list[float]]:
    """`count` points `r` from the centre, evenly all around, the first one ahead of the nose.

    Where the Hive's rings leave from (ENM-HIVE-10): fixed barrels (`[x, y, height, angle]`, the
    angle in degrees from the nose, positive to the right as headings are, so negative for a point
    on the screen's right when it faces down).
    """
    return [
        [
            r * math.sin((2 * math.pi * k) / count),
            -r * math.cos((2 * math.pi * k) / count),
            height,
            -360 * k / count,
        ]
        for k in range(count)
    ]


def fold_entries(entries: list[Any]) -> Any:
    """`Object.fromEntries`: an object of the [key, value] pairs in `entries`."""
    result: dict[str, Any] = {}
    for entry in entries:
        result[entry[0]] = entry[1]
    return result


def swing(amplitude_deg: float, period: float, phase: float) -> Any:
    """Return a joint's swing: `amplitudeDeg` each way, every `period` s.

    It runs `phase` of a turn later.
    """
    return record({"amplitudeDeg": amplitude_deg, "period": period, "phase": phase})


# ENM-HYDRA-08: the Hydra's necks: each a joint at the hull's front, its head at the end.
HYDRA_NECKS = [
    record({"side": "left", "pivot": [-8, -5], "head": [-19, -21]}),
    record({"side": "middle", "pivot": [0, -7], "head": [0, -25]}),
    record({"side": "right", "pivot": [8, -5], "head": [19, -21]}),
]
HYDRA_HEAD = record({"radius": 6.5, "health": 50, "eyeAhead": 5, "eyeHeight": 3})


def hydra_heads() -> list[Any]:
    """Return the Hydra's heads, one per neck."""
    heads: list[Any] = []
    for i, neck in enumerate(HYDRA_NECKS):
        pivot = neck["pivot"]
        head = neck["head"]
        aim = aim_from(pivot, head)
        eye = along_aim(head, aim, HYDRA_HEAD.eyeAhead)
        heads.append(
            record({
                "id": "head-" + neck["side"],
                "joint": "neck-" + neck["side"],
                "pivot": pivot,
                "head": head,
                "aim": aim,
                # Its eye, where its bullets leave from.
                "muzzle": [eye[0], eye[1], HYDRA_HEAD.eyeHeight],
                # The necks sway out of step.
                "phase": i / len(HYDRA_NECKS),
            })
        )
    return heads


HYDRA_HEADS = hydra_heads()

# ENM-SCISSOR-09: the Scissor's arms: hinged at the shoulders, 25 degrees out from straight down
# at rest.
SCISSOR_ARM = record({"length": 30, "spread": 25, "partAt": 16, "height": 2})


def scissor_arms() -> list[Any]:
    """Return the Scissor's two arms, left then right."""
    arms: list[Any] = []
    for s in [-1, 1]:
        pivot = [s * 6, 2]
        # Right arm (s = 1): pointing down and to the right, anticlockwise from the nose.
        aim = -s * SCISSOR_ARM.spread * DEG
        centre = along_aim(pivot, aim, SCISSOR_ARM.partAt)
        tip = along_aim(pivot, aim, SCISSOR_ARM.length)
        arms.append(
            record({
                "id": "arm-left" if s < 0 else "arm-right",
                "joint": "shoulder-left" if s < 0 else "shoulder-right",
                "pivot": pivot,
                "centre": centre,
                "aim": aim,
                # Its emitter at the tip, where its laser leaves from.
                "muzzle": [tip[0], tip[1], SCISSOR_ARM.height],
                # Its swing turns it inward first (clockwise for the right arm).
                "phase": 0.5 if s < 0 else 0,
            })
        )
    return arms


SCISSOR_ARMS = scissor_arms()

# ENM-JUGGERNAUT-09, ENM-JUGGERNAUT-12: the Juggernaut's shoulder cannons and front plates.
JUGGERNAUT_CANNONS = [
    record({
        "id": "cannon-left" if s < 0 else "cannon-right",
        "joint": "shoulder-left" if s < 0 else "shoulder-right",
        "pivot": [s * 22, 3],
        "centre": [s * 28, -3],
        # The tip of its barrel: its bursts leave from there, along it.
        "muzzle": [s * 28, -16, 3],
        "phase": 0.5 if s < 0 else 0,
    })
    for s in [-1, 1]
]
JUGGERNAUT_PLATES = [
    record({"id": "plate-left" if s < 0 else "plate-right", "x": s * 10, "y": -17}) for s in [-1, 1]
]


ELITE_CONFIG = record({
    # ENM-HYDRA-11: health, points and hit circle.
    "hydra": {
        "stats": {"model": "hydra", "radius": 17, "health": 220, "points": 700},
        "size": 1.6,
        "entrySpeed": 75,
        # It stops in the upper third.
        "stopFraction": 0.74,
        "stay": 7,
        "exitSpeed": 95,
        # One head launches a missile every `headFireInterval`, in turn; the first after
        # `firstShot` (ENM-HYDRA-09).
        "headFireInterval": 0.8,
        "firstShot": 0.5,
        # Homing missiles, a little slower than the Rocketeer's (ENM-HYDRA-14).
        "missile": {
            "speed": 130,
            "turnRateDeg": 90,
            "homingSeconds": 3.5,
            "radius": 5,
            "health": 10,
            "style": "rocketeer",
        },
        "heads": HYDRA_HEADS,
        "design": {
            "joints": fold_entries([
                [
                    h["joint"],
                    {
                        "x": h["pivot"][0],
                        "y": h["pivot"][1],
                        "swing": swing(16, 2.6, h["phase"]),
                    },
                ]
                for h in HYDRA_HEADS
            ]),
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
    # ENM-SCISSOR-14: health, points and hit circle.
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
            "joints": fold_entries([
                [
                    a["joint"],
                    # A quarter of a period is the firing time: the arm closes by `sweep`
                    # (ENM-SCISSOR-11).
                    {
                        "x": a["pivot"][0],
                        "y": a["pivot"][1],
                        "swing": swing(15, 8, a["phase"]),
                    },
                ]
                for a in SCISSOR_ARMS
            ]),
            # The arms as parts (ENM-SCISSOR-13).
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
    # ENM-JUGGERNAUT-14: health, points and hit circle.
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
        # ENM-JUGGERNAUT-11: seven parallel barrels in the mantlet of its back turret (on the
        # turret, WPN-02). The turret turns at `turret.turnDeg` and sweeps the spread: each
        # barrel fires in turn, `sweepGap` after the one before, once the turret points that
        # bullet's way.
        "muzzles": [[(3 - i) * 1.6, -9, 8.8] for i in range(7)],
        "turret": {"x": 0, "y": 3, "turnDeg": 240},
        "sweepGap": 0.08,
        # Each shoulder cannon fires a burst of `burstCount` along its barrel every interval.
        "cannonInterval": 1.6,
        "firstBurst": 0.8,
        "burstCount": 3,
        "burstGap": 0.12,
        "cannonBullet": bullet("blue", 210),
        "cannons": JUGGERNAUT_CANNONS,
        "plates": JUGGERNAUT_PLATES,
        "design": {
            "joints": fold_entries([
                [
                    c["joint"],
                    {
                        "x": c["pivot"][0],
                        "y": c["pivot"][1],
                        "swing": swing(20, 2.4, c["phase"]),
                    },
                ]
                for c in JUGGERNAUT_CANNONS
            ]),
            # The cannons as parts (ENM-JUGGERNAUT-13); while a plate stands, the core cannot
            # be hit (ENM-JUGGERNAUT-12).
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
    # ENM-HIVE-12: health, points and hit circle.
    "hive": {
        "stats": {"model": "hive", "radius": radius(2) * 0.8, "health": 420, "points": 900},
        "size": 2,
        "speed": 28,
        # How fast its launch ring turns, degrees per second.
        "ringSpin": 45,
        # A Splitter from the ring every `launchInterval`, the first after `firstLaunch`.
        "launchInterval": 6,
        "firstLaunch": 2,
        # The ring's launch hatch, on the turning ring: Splitters come out of it.
        "port": [0, 14, 9],
        # A launched Splitter flies this far down from the hatch before its pause.
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
})
