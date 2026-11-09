# Copyright (c) 2026 Renaud Guillon
"""Tunables of the Broodmother (`specs/enemies/broodmother.md`), the carrier of tier 3.

Distances in logical pixels, speeds in px/s, times in seconds. `...Fraction` heights are fractions
of the playfield height from its bottom (ENM-BROODMOTHER-11).
"""

from game.config.enemies import bullet
from game.config.enemies_elite import radius
from game.config.enemy_tiers import TIER_DAMAGE
from game.config.record import record

BROODMOTHER_CONFIG = record({
    # ENM-BROODMOTHER-11: health, points and hit circle.
    "stats": {
        "model": "broodmother",
        "radius": radius(3) * 0.8,
        "health": 880,
        "points": 1200,
    },
    # A flying aircraft carrier, big enough for a Phantom's launch bay in its deck.
    "size": 3,
    "speed": 22,
    # A Phantom from the bay every `launchInterval`, the first after `firstLaunch`.
    "launchInterval": 7,
    "firstLaunch": 2.5,
    # Where its Phantom takes off from: just out of the mouth of the hangar at its stern, on the
    # runway, from the carrier's centre (X right, Y up the screen: negative is down it). The model
    # rolls it out of the hangar to there (ENM-BROODMOTHER-02).
    "port": [0, 12],
    # A launched Phantom flies this far below where it took off, clear of the bow, before its
    # first stop.
    "launchDrop": 100,
    # The Phantom in the hangar starts rolling out `rollSeconds` before a launch, reaching the
    # take-off point as it launches; the next one shows in the hangar `reloadDelay` s after.
    "hangar": {"rollSeconds": 1.6, "reloadDelay": 0.8},
    # Its gun turret on the raised shoulder on its left (the screen's): its pivot from its centre
    # (X right, Y up the screen), how far ahead of it the barrel's tip is at rest (pointing down the
    # screen) and how high; it turns towards the player at `turnDeg` per second and fires once it
    # points at them, a shot every `fireInterval`, the first `firstShot` after it shows.
    "turrets": {
        # Half as big again as the Hatchery's and standing on the shoulder: the model's
        # `TURRET_SIZE` (scale 1.5, lift 3.75) sets the barrel's height and length.
        "pivots": [[-26.5, 12]],
        "barrel": 14,
        "height": 4.35,
        "turnDeg": 100,
        "fireInterval": 1.6,
        "firstShot": 1,
        "bullet": bullet("green", 190, TIER_DAMAGE["3"].bullet),
    },
    # It stops launching below this height, too close to the player.
    "lastFraction": 0.3,
    "xRange": [0.3, 0.7],
})
