# Copyright (c) 2026 Renaud Guillon
"""Tunables of the Hatchery (`specs/enemies/hatchery.md`), the carrier of tier 2.

In the units of `enemies.py`: logical pixels, px/s, seconds; `...Fraction` heights are fractions of
the playfield height from its bottom.
"""

from game.config.enemies import radius
from game.config.record import record

HATCHERY_CONFIG = record({
    # ENM-HATCHERY-09: health, points and hit circle.
    "stats": {"model": "hatchery", "radius": radius(1.7) * 0.8, "health": 400, "points": 700},
    "size": 1.7,
    "speed": 32,
    # A group of Wasps from the hatch every `launchInterval`, the first after `firstLaunch`.
    "launchInterval": 6,
    "firstLaunch": 2.5,
    # The ventral hatch, from its centre (X right, Y up the screen, height): towards the player's
    # side, where the Wasps come out. The model draws it there (ENM-HATCHERY-02).
    "hatch": [0, -14, 0],
    # Where each Wasp of a group comes out, from the hatch: across and up the screen.
    "group": [[-13, 0], [0, -7], [13, 0]],
    # A launched Wasp flies this far down from its start before its pause.
    "launchDrop": 55,
    # It stops launching below this height, too close to the player (ENM-HATCHERY-08).
    "lastLaunchFraction": 0.3,
    "xRange": [0.3, 0.7],
})
