# Copyright (c) 2026 Renaud Guillon
"""Tunables of the Hatchery (`specs/enemies/hatchery.md`), the carrier of tier 2.

In the units of `enemies.py`: logical pixels, px/s, seconds; `...Fraction` heights are fractions of
the playfield height from its bottom.
"""

from game.config.enemies import bullet, radius
from game.config.record import record

HATCHERY_CONFIG = record({
    # ENM-HATCHERY-09: health, points and hit circle.
    "stats": {"model": "hatchery", "radius": radius(2.2) * 0.8, "health": 400, "points": 700},
    "size": 2.2,
    "speed": 32,
    # A Wasp from each bay every `launchInterval`, the first after `firstLaunch`.
    "launchInterval": 6,
    "firstLaunch": 2.5,
    # The three launch bays on its deck, open to the sky, from its centre (X right, Y up the
    # screen): a Wasp waits in each and takes off from there. The model draws them there
    # (ENM-HATCHERY-02).
    "bays": [[0, 20], [0, 0], [0, -20]],
    # A launched Wasp flies this far down from its bay before its pause.
    "launchDrop": 70,
    # The bays' doors: they start opening `openLead` s before a launch and take `seconds` to open
    # or close; the Wasp then rises to the deck in `riseSeconds`. After a launch they stay open
    # `closeDelay` s before closing.
    "doors": {"openLead": 1.5, "seconds": 0.5, "riseSeconds": 0.6, "closeDelay": 0.35},
    # A gun turret on each side (ENM-HATCHERY-06 review): their pivots from its centre (X right,
    # Y up the screen), how far ahead of its pivot a barrel's tip is at rest (pointing down the
    # screen) and how high; each turns towards the player at `turnDeg` per second and fires once it
    # points at them, a shot each every `fireInterval`, the first `firstShot` after it shows.
    "turrets": {
        "pivots": [[-23, 0], [23, 0]],
        "barrel": 9.3,
        "height": 0.4,
        "turnDeg": 110,
        "fireInterval": 1.8,
        "firstShot": 1.2,
        "bullet": bullet("green", 190),
    },
    # It stops launching below this height, too close to the player (ENM-HATCHERY-08).
    "lastLaunchFraction": 0.3,
    "xRange": [0.3, 0.7],
})
