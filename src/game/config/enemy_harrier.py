# Copyright (c) 2026 Renaud Guillon
"""Tunables of the Harrier (`specs/enemies/harrier.md`), the missile launcher of tier 2.

In the units of `enemies.py`: logical pixels, px/s, seconds, degrees; `...Fraction` heights are
fractions of the playfield height from its bottom; `muzzles` are offsets from the centre facing
down the screen (X right, Y up, and a height).
"""

from game.config.enemies import radius
from game.config.record import record

# Distance of each launcher from its centre, out on its shoulder pod.
HARRIER_RAIL = 8

HARRIER_CONFIG = record({
    # ENM-HARRIER-09: health, points and hit circle.
    "stats": {"model": "harrier", "radius": radius(0.9), "health": 60, "points": 220},
    "size": 0.9,
    "entrySpeed": 260,
    # It slows down over this distance before its stop point.
    "brakeDistance": 90,
    "stopFraction": 0.78,
    # How fast it strafes sideways while it holds, and how far from the side edges it turns back.
    "strafeSpeed": 28,
    "strafeMargin": 40,
    # A missile every `fireInterval`, the first `firstShot` after it holds; it leaves after
    # `missiles` of them.
    "fireInterval": 2.5,
    "firstShot": 0.8,
    "missiles": 4,
    "exitSpeed": 280,
    # The mouths of its two launchers on its shoulder pods: the missiles leave from each in turn
    # (ENM-HARRIER-02).
    "muzzles": [
        [-HARRIER_RAIL, -12, 0],
        [HARRIER_RAIL, -12, 0],
    ],
    # A fast, tight homing missile (ENM-HARRIER-07), faster and tighter than the Rocketeer's.
    "missile": {
        "speed": 240,
        "turnRateDeg": 150,
        "homingSeconds": 2.5,
        "radius": 4,
        "health": 10,
        "style": "rocketeer",
    },
    "xRange": [0.2, 0.8],
})
