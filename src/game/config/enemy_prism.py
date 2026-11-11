# Copyright (c) 2026 Renaud Guillon
"""Tunables of the Prism (`specs/enemies/prism.md`), the laser kind of tier 3 (ENM-PRISM-12).

Distances in logical pixels, speeds in px/s, times in seconds, angles in degrees. `...Fraction`
heights are fractions of the playfield height from its bottom. Muzzles as in `enemies.py` (x, y,
height).
"""

from game.config.enemies_elite import radius
from game.config.enemy_tiers import TIER_DAMAGE
from game.config.record import record

# Where each wing's emitter is: out from the centre, ahead of it (a muzzle's Y is negative ahead),
# and its height above the playfield.
EMITTER_X = 21
EMITTER_AHEAD = 21
EMITTER_HEIGHT = 2.5

PRISM_CONFIG = record({
    # ENM-PRISM-12: health, points and hit circle.
    "stats": {"model": "prism", "radius": radius(1.5) * 0.8, "health": 190, "points": 380},
    "size": 1.5,
    "entrySpeed": 320,
    # It slows down over this distance before its stop point, turning to the player as it does.
    "brakeDistance": 220,
    # Its stop height: one at random in this range (D-313).
    "stopRange": [0.45, 0.8],
    "exitSpeed": 180,
    # Each emitter's laser: 1 s of warning line, then 2 s of beam, both straight ahead.
    "laser": {
        "warningSeconds": 1,
        "firingSeconds": 2,
        "width": 9,
        "style": "lancer",
        "damage": TIER_DAMAGE["3"].laser,
    },
    # How many bursts it fires, one after the other.
    "bursts": 2,
    # Before each burst it turns its nose to the player for this long; it stops turning when the
    # warning lines show.
    "aimSeconds": 1,
    # The emitters at the wings' tips, left then right.
    "emitters": [
        [-EMITTER_X, -EMITTER_AHEAD, EMITTER_HEIGHT],
        [EMITTER_X, -EMITTER_AHEAD, EMITTER_HEIGHT],
    ],
    "xRange": [0.25, 0.75],
})
