# Copyright (c) 2026 Renaud Guillon
"""Tunables of the Sweeper (`specs/enemies/sweeper.md`), the laser of tier 2.

In the units of `enemies.py`: logical pixels, px/s, seconds, degrees; `...Fraction` heights are
fractions of the playfield height from its bottom.
"""

from game.config.enemies import ENEMY_UNIT, radius
from game.config.record import record

# The tip of its emitter barrel, ahead of its centre.
SWEEPER_BARREL = 0.62 * ENEMY_UNIT

SWEEPER_CONFIG = record({
    # ENM-SWEEPER-09: health, points and hit circle.
    "stats": {"model": "sweeper", "radius": radius(1.3) * 0.8, "health": 90, "points": 300},
    "size": 1.3,
    "entrySpeed": 150,
    # It slows down over this distance before its stop point.
    "brakeDistance": 60,
    "stopFraction": 0.78,
    # The warning line shows along the beam's first heading for `warningSeconds`; then the beam
    # turns across `arcDeg` over `firingSeconds` (ENM-SWEEPER-06).
    "laser": {"warningSeconds": 1, "firingSeconds": 2.2, "width": 9, "style": "lancer"},
    "arcDeg": 70,
    # Distance from the centre to the tip of the barrel, and the barrel's front, where the laser
    # leaves from (with a height above the playfield).
    "barrelOffset": SWEEPER_BARREL,
    "muzzle": [0, -(SWEEPER_BARREL + 1.8), 7],
    "exitSpeed": 200,
    "xRange": [0.25, 0.75],
})
