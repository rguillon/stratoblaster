# Copyright (c) 2026 Renaud Guillon
"""Tunables of the Broodmother (`specs/enemies/broodmother.md`), the carrier of tier 3.

Distances in logical pixels, speeds in px/s, times in seconds. `...Fraction` heights are fractions
of the playfield height from its bottom (ENM-BROODMOTHER-11).
"""

from game.config.enemies_elite import radius
from game.config.record import record

BROODMOTHER_CONFIG = record({
    # ENM-BROODMOTHER-11: health, points and hit circle.
    "stats": {
        "model": "broodmother",
        "radius": radius(2) * 0.8,
        "health": 700,
        "points": 1200,
    },
    "size": 2,
    "speed": 22,
    # A Phantom from the hatch every `launchInterval`, the first after `firstLaunch`.
    "launchInterval": 7,
    "firstLaunch": 2.5,
    # The hatch on its belly: out from the centre, ahead of it (negative Y is down the screen).
    "port": [0, -22],
    # A launched Phantom comes in to this far below the hatch.
    "launchDrop": 60,
    # It stops launching below this height, too close to the player.
    "lastFraction": 0.3,
    "xRange": [0.3, 0.7],
})
