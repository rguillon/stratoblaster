"""Tunables of the first enemies (P05)

Distances in logical pixels, speeds in px/s, times in seconds, angles in degrees. Heights given as
`...Fraction` are fractions of the playfield height from its bottom (1 = top edge).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# `L`: length of the medium (balanced) player ship on the playfield, ~4.8 model units x 7.
ENEMY_UNIT = 34

# Hit radius relative to half the model size (GD-21: a hitbox about as big as the model).
HITBOX = 0.85


def radius(size: float) -> float:
    """Hit radius of an enemy `size` L across."""
    return (size * ENEMY_UNIT * HITBOX) / 2


# How far above the top edge (or beside the side edges) enemies appear.
ENEMY_SPAWN_MARGIN = 60


def bullet(style: str, speed: float) -> Any:
    """Enemy bullets: colourful glowing balls (GD-43). The style keys the look in `enemy_look`."""
    return record({"speed": speed, "radius": 4, "style": style})


# `muzzles` (phase 7 review): where the shots leave from, the tips of the barrels the models draw
# there: offsets from the centre as seen when the enemy faces down the screen (X right, Y up), and
# heights above the playfield (see `core/entities/muzzle.py`).

# The Spinner's pods' muzzles, out from its centre.
SPINNER_MUZZLE = 0.45 * ENEMY_UNIT + 3.1
# The Lancer's emitter, ahead of its centre.
LANCER_NOSE = 0.62 * ENEMY_UNIT
# The Rocketeer's pods, either side of its centre.
ROCKETEER_POD = 0.48 * ENEMY_UNIT

ENEMY_CONFIG = record(
    {
        "gnat": {
            "stats": {"model": "gnat", "radius": radius(0.5), "health": 10, "points": 50},
            "size": 0.5,
            "groupSize": 5,
            "groupDelay": 0.3,
            "speed": 190,
            # S-shaped path, as fractions of the playfield (x across, y up); mirrored at random.
            "path": [
                [0.75, 1.1],
                [0.75, 0.85],
                [0.25, 0.65],
                [0.75, 0.4],
                [0.25, 0.18],
                [0.4, -0.15],
            ],
        },
        "hornet": {
            "stats": {"model": "hornet", "radius": radius(0.7), "health": 20, "points": 100},
            "size": 0.7,
            "entrySpeed": 220,
            # Height where it stops before diving.
            "stopFraction": 0.72,
            # Deceleration into the stop: about 0.45 s and 55 px of braking from the entry speed.
            "entryBrake": 440,
            "pause": 0.5,
            "diveAcceleration": 1000,
            "diveMaxSpeed": 620,
            # Range of X where it appears, as fractions of the width.
            "xRange": [0.15, 0.85],
        },
        "scout": {
            "stats": {"model": "scout", "radius": radius(0.8), "health": 30, "points": 100},
            "size": 0.8,
            "speed": 75,
            "fireInterval": 1.5,
            # Delay before the first shot once on the playfield.
            "firstShot": 0.6,
            "bullet": bullet("red", 210),
            # The nose gun.
            "muzzles": [[0, -13.3, 1.3]],
            "xRange": [0.15, 0.85],
        },
        "strafer": {
            "stats": {
                "model": "strafer",
                "radius": radius(1.2) * 0.75,
                "health": 40,
                "points": 150,
            },
            "size": 1.2,
            "speed": 150,
            # Height of its pass, in the top third.
            "heightFraction": 0.8,
            "fireInterval": 1,
            "fanCount": 3,
            "fanSpacing": 15,
            "bullet": bullet("magenta", 200),
            # A gun on each side of its body: it fires from the one facing down the screen.
            "muzzles": [
                [9, -1.5, 1.5],
                [-9, -1.5, 1.5],
            ],
        },
        "weaver": {
            "stats": {"model": "weaver", "radius": radius(0.9), "health": 30, "points": 120},
            "size": 0.9,
            "speed": 85,
            "amplitude": 90,
            # Distance travelled down for one full left-right sway.
            "wavelength": 280,
            "fireInterval": 2,
            # A gun on the nose of each hull: a bullet from each.
            "muzzles": [
                [-10, -15.8, 1.9],
                [10, -15.8, 1.9],
            ],
            "bullet": bullet("green", 200),
            "xRange": [0.3, 0.7],
        },
        "spinner": {
            "stats": {"model": "spinner", "radius": radius(1), "health": 60, "points": 200},
            "size": 1,
            "entrySpeed": 130,
            # It stops at a random height between these (the upper half).
            "stopRange": [0.62, 0.8],
            "idleSpin": 60,
            "firingSpin": 110,
            "fireDuration": 3,
            # Seconds between two bullets from each pod.
            "fireInterval": 0.16,
            "pods": 4,
            # Distance of the pods from the centre.
            "podRadius": 0.45 * ENEMY_UNIT,
            "exitSpeed": 150,
            "bullet": bullet("orange", 160),
            # The pods' muzzles: each bullet leaves outwards from the pod facing its way.
            "muzzles": [
                [0, -SPINNER_MUZZLE, 0],
                [-SPINNER_MUZZLE, 0, 0],
                [0, SPINNER_MUZZLE, 0],
                [SPINNER_MUZZLE, 0, 0],
            ],
            "xRange": [0.25, 0.75],
        },
        "lancer": {
            "stats": {"model": "lancer", "radius": radius(1.3) * 0.55, "health": 80, "points": 250},
            "size": 1.3,
            "entrySpeed": 170,
            # It slows down over this distance before its stop point.
            "brakeDistance": 60,
            "stopFraction": 0.8,
            "laser": {"warningSeconds": 1, "firingSeconds": 1.5, "width": 10, "style": "lancer"},
            # Distance from the centre to the emitter at the nose.
            "emitterOffset": LANCER_NOSE,
            # The front of the emitter, where the laser leaves from.
            "muzzle": [0, -(LANCER_NOSE + 1.8), 0],
            "exitSpeed": 200,
            "xRange": [0.15, 0.85],
        },
        "rocketeer": {
            "stats": {
                "model": "rocketeer",
                "radius": radius(1.3) * 0.8,
                "health": 100,
                "points": 300,
            },
            "size": 1.3,
            "speed": 45,
            "fireInterval": 3,
            "firstShot": 1,
            # Distance of each pod from the centre.
            "podOffset": ROCKETEER_POD,
            # The pods' missile tips: a missile from each.
            "muzzles": [
                [-ROCKETEER_POD, -14.5, 0],
                [ROCKETEER_POD, -14.5, 0],
            ],
            "missile": {
                "speed": 150,
                "turnRateDeg": 90,
                "homingSeconds": 3.5,
                "radius": 5,
                "health": 10,
                "style": "rocketeer",
            },
            "xRange": [0.2, 0.8],
        },
        "bulwark": {
            "stats": {
                "model": "bulwark",
                "radius": radius(1.6) * 0.8,
                "health": 200,
                "points": 500,
            },
            "size": 1.6,
            "entrySpeed": 70,
            "stopFraction": 0.74,
            "drift": 70,
            # Seconds for one left-right drift.
            "driftPeriod": 4,
            "stay": 8,
            "exitSpeed": 90,
            "fireInterval": 2,
            "spreadCount": 5,
            "spreadSpacing": 10,
            "bullet": bullet("blue", 190),
            # The twin cannon on the front of its tower.
            "muzzles": [
                [-3, -14, 4.2],
                [3, -14, 4.2],
            ],
            "xRange": [0.3, 0.7],
        },
        "splitter": {
            "stats": {"model": "splitter", "radius": radius(1), "health": 50, "points": 200},
            "size": 1,
            "speed": 95,
            "fireInterval": 2.5,
            "firstShot": 0.8,
            "bullet": bullet("purple", 200),
            # The eye on top of its core.
            "muzzles": [[0, 0, 5.4]],
            # Curved path, fractions of the playfield; mirrored at random.
            "path": [
                [0.2, 1.1],
                [0.3, 0.7],
                [0.65, 0.45],
                [0.8, -0.15],
            ],
            # Distance of the three pods from the centre.
            "podOffset": 0.38 * ENEMY_UNIT,
        },
        "carrier": {
            "stats": {
                "model": "carrier",
                "radius": radius(1.8) * 0.8,
                "health": 300,
                "points": 600,
            },
            "size": 1.8,
            "speed": 30,
            # A Gnat from each side port every `launchInterval`, the first after `firstLaunch`.
            "launchInterval": 3,
            "firstLaunch": 1.2,
            # The launch ports on its right side (mirrored on the left), from its centre: out to
            # the side and up the screen, in px. The model puts its ports there.
            "ports": [
                [21, 9],
                [21, -1],
            ],
            # It stops launching below this height, too close to the player.
            "lastLaunchFraction": 0.3,
            # The launched Gnats' path from a port, in px, for the right side (mirrored for the
            # left): out sideways, then down past the bottom of the screen.
            "launchPath": [
                [0, 0],
                [28, -4],
                [55, -30],
                [64, -110],
                [40, -260],
                [20, -800],
            ],
            "xRange": [0.3, 0.7],
        },
        # The pods a destroyed Splitter breaks into: small Hornets (P05-R10).
        "splitterPod": {
            "stats": {
                "model": "splitter-pod",
                "radius": radius(0.4),
                "health": 10,
                "points": 50,
            },
            "size": 0.4,
            "pause": 0.35,
            "diveAcceleration": 950,
            "diveMaxSpeed": 560,
        },
    }
)
