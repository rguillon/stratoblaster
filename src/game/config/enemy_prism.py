# Copyright (c) 2026 Renaud Guillon
"""Tunables of the Prism (`specs/enemies/prism.md`), the laser kind of tier 3 (ENM-PRISM-12).

Distances in logical pixels, speeds in px/s, times in seconds, angles in degrees. `...Fraction`
heights are fractions of the playfield height from its bottom. Muzzles as in `enemies.py` (x, y,
height).
"""

from game.config.enemies_elite import radius
from game.config.record import record

# Where each wing's emitter is: out from the centre, ahead of it (a muzzle's Y is negative ahead),
# and its height above the playfield.
EMITTER_X = 21
EMITTER_AHEAD = 4
EMITTER_HEIGHT = 2.5

PRISM_CONFIG = record({
    # ENM-PRISM-12: health, points and hit circle.
    "stats": {"model": "prism", "radius": radius(1.5) * 0.8, "health": 150, "points": 380},
    "size": 1.5,
    "entrySpeed": 150,
    # It slows down over this distance before its stop point.
    "brakeDistance": 60,
    # It stops in the upper third.
    "stopFraction": 0.78,
    "exitSpeed": 180,
    # Each emitter's laser: 1 s of warning line, then 2 s of beam turning with its emitter.
    "laser": {"warningSeconds": 1, "firingSeconds": 2, "width": 9, "style": "lancer"},
    # The two bursts. A beam's angle goes from `start` to `end` while it fires, in degrees from
    # straight down, positive outward (away from the other beam), negative inward past it: the
    # first burst closes into an X, the second opens it again, the crossing sliding down the screen.
    "bursts": [{"start": 50, "end": -35}, {"start": -35, "end": 50}],
    # The pause between the two bursts.
    "gapSeconds": 0.6,
    # The emitters at the wings' tips, left then right.
    "emitters": [
        [-EMITTER_X, -EMITTER_AHEAD, EMITTER_HEIGHT],
        [EMITTER_X, -EMITTER_AHEAD, EMITTER_HEIGHT],
    ],
    "xRange": [0.25, 0.75],
})
