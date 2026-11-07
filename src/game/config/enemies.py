# Copyright (c) 2026 Renaud Guillon
"""Tunables of the basic enemies (ENM-06; each kind's file in specs/enemies/).

Points follow each kind's difficulty (GAME-SCORE-03); a new look changes none of these (ENM-46).
Distances in logical pixels, speeds in px/s, times in seconds, angles in degrees. Heights given as
`...Fraction` are fractions of the playfield height from its bottom (1 = top edge).
"""

import math

from game.config.record import record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# `L` (ENM-05): length of the medium (balanced) player ship on the playfield, ~4.8 model units x 7.
ENEMY_UNIT = 34

# Hit radius relative to half the model size (ENM-11: a hitbox about as big as the model).
HITBOX = 0.85


def radius(size: float) -> float:
    """Hit radius of an enemy `size` L across."""
    return (size * ENEMY_UNIT * HITBOX) / 2


# How far above the top edge (or beside the side edges) enemies appear (ENM-07).
ENEMY_SPAWN_MARGIN = 60


def bullet(style: str, speed: float) -> Any:
    """Enemy bullets: colourful glowing balls (ENM-16). The style keys the look in `enemy_look`."""
    return record({"speed": speed, "radius": 4, "style": style})


# `muzzles` (phase 7 review): where the shots leave from, the tips of the barrels the models draw
# there: offsets from the centre as seen when the enemy faces down the screen (X right, Y up), and
# heights above the playfield (see `core/entities/muzzle.py`).

# The Strafer's fixed barrels (WPN-04): three on each side of its body, fanned `STRAFER_FAN` degrees
# apart, each `STRAFER_BARREL` long (plus its muzzle's charge light) from a base on the flank, one
# above the other along it. Each muzzle is `[x, y, height, angle]`: its tip, and the angle the
# barrel points at from the nose, in degrees (positive to the right), as `Barrel` reads it.
STRAFER_FAN = 15
STRAFER_FLANK = 4.6
STRAFER_BARREL = 6.2
STRAFER_ROWS = [3.8, 1.6, -0.6]


def strafer_barrels() -> list[list[float]]:
    """Return the Strafer's six barrels: each side's fan of three, as `[x, y, height, angle]`."""
    barrels: list[list[float]] = []
    for side in [1, -1]:
        for k, fan in enumerate([STRAFER_FAN, 0, -STRAFER_FAN]):
            # Pointing out sideways, turned `fan` towards the nose; the sim angle is the model's
            # yaw negated.
            yaw = math.radians(90 - fan)
            tip_x = side * (STRAFER_FLANK + math.sin(yaw) * STRAFER_BARREL)
            tip_y = -(STRAFER_ROWS[k] + math.cos(yaw) * STRAFER_BARREL)
            barrels.append([tip_x, tip_y, 1.5, -side * (90 - fan)])
    return barrels


def fan_barrels(
    count: int, spacing: float, gap: float, y: float, height: float
) -> list[list[float]]:
    """Return `count` fixed barrels side by side, fanned `spacing` degrees apart (WPN-01).

    Their tips `gap` apart at `y` and `height`; the barrel turned `k` fans to the right (a positive
    angle) is on the left of the nose (screen X is negative), so they diverge.
    """
    barrels: list[list[float]] = []
    for i in range(count):
        k = i - (count - 1) / 2
        barrels.append([-k * gap, y, height, k * spacing])
    return barrels


# The Spinner's pods' muzzles, out from its centre.
SPINNER_MUZZLE = 0.45 * ENEMY_UNIT + 3.1
# The Lancer's emitter, ahead of its centre.
LANCER_NOSE = 0.62 * ENEMY_UNIT
# The Rocketeer's pods, either side of its centre.
ROCKETEER_POD = 0.48 * ENEMY_UNIT

ENEMY_CONFIG = record({
    # ENM-HORNET-04 (entry and braking), ENM-HORNET-09 (health and points).
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
    # ENM-SCOUT-07: health and points.
    "scout": {
        "stats": {"model": "scout", "radius": radius(0.8), "health": 30, "points": 100},
        "size": 0.8,
        "speed": 75,
        "fireInterval": 1.5,
        # Delay before the first shot once on the playfield.
        "firstShot": 0.6,
        "bullet": bullet("red", 210),
        # The nose gun (ENM-SCOUT-03).
        # Its gun's tip: a 9 px barrel from the turret's pivot, behind the wings' roots (D-276).
        "muzzles": [[0, -7.8, 4.9]],
        # Its gun turns on a pivot at the barrel's root to face the player before it fires (WPN-02).
        "turret": {"x": 0, "y": 2, "turnDeg": 150},
        "xRange": [0.15, 0.85],
    },
    # ENM-STRAFER-07: health and points.
    "strafer": {
        "stats": {
            "model": "strafer",
            "radius": radius(1.2) * 0.75,
            "health": 40,
            "points": 150,
        },
        "size": 1.2,
        "speed": 150,
        # Height of its side pass, in the top third.
        "heightFraction": 0.8,
        # Range of X of its vertical pass from the top, as fractions of the width.
        "xRange": [0.12, 0.88],
        "fireInterval": 1,
        "fanCount": 3,
        "fanSpacing": 15,
        "bullet": bullet("magenta", 200),
        # Three guns on each side of its body (ENM-STRAFER-03, WPN-04): the three of the side facing
        # down the screen fire, one shot each.
        "muzzles": strafer_barrels(),
    },
    # ENM-SPINNER-07: health and points.
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
            [0, -SPINNER_MUZZLE, 0, 0],
            [-SPINNER_MUZZLE, 0, 0, 90],
            [0, SPINNER_MUZZLE, 0, 180],
            [SPINNER_MUZZLE, 0, 0, -90],
        ],
        "xRange": [0.25, 0.75],
    },
    # ENM-LANCER-08: health and points.
    "lancer": {
        "stats": {"model": "lancer", "radius": radius(1.3) * 0.55, "health": 80, "points": 250},
        "size": 1.3,
        # It comes in at `entrySpeed`, then flies at `cruiseSpeed` between its stops, speeding
        # up at `acceleration` and braking at `brake` (px/s, px/s²).
        "entrySpeed": 170,
        "cruiseSpeed": 140,
        "acceleration": 120,
        "brake": 150,
        # Its first stop, as a fraction of the height; each next stop is `stepFraction` of the
        # height lower, none under `lastStopFraction` (it leaves through the bottom instead).
        "stopFraction": 0.8,
        "stepFraction": 0.25,
        "lastStopFraction": 0.25,
        "laser": {"warningSeconds": 1, "firingSeconds": 1.5, "width": 10, "style": "lancer"},
        # Distance from the centre to the emitter at the nose.
        "emitterOffset": LANCER_NOSE,
        # The front of the emitter, where the laser leaves from.
        "muzzle": [0, -(LANCER_NOSE + 1.8), 0],
        # Its top speed down and out of the bottom of the screen after its last shot.
        "exitSpeed": 200,
        "xRange": [0.15, 0.85],
    },
    # ENM-ROCKETEER-09: health and points.
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
        # The pods' missile tips: a missile from each (ENM-ROCKETEER-06).
        "muzzles": [
            [-ROCKETEER_POD, -14.5, 0],
            [ROCKETEER_POD, -14.5, 0],
        ],
        # Homing missiles (ENM-ROCKETEER-07).
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
    # ENM-SPLITTER-09: health and points. Tier 4's diver (ENM-SPLITTER-05): like a Hornet, but
    # bigger and tougher, and it never shoots.
    "splitter": {
        "stats": {"model": "splitter", "radius": radius(1), "health": 200, "points": 450},
        "size": 1,
        "entrySpeed": 150,
        # Height where it stops before diving, in the upper half.
        "stopFraction": 0.7,
        # Deceleration into the stop.
        "entryBrake": 300,
        "pause": 0.7,
        "diveAcceleration": 800,
        "diveMaxSpeed": 480,
        # Distance of the three pods from the centre.
        "podOffset": 0.38 * ENEMY_UNIT,
        "xRange": [0.2, 0.8],
    },
    # ENM-CARRIER-10: health and points.
    "carrier": {
        "stats": {
            "model": "carrier",
            "radius": radius(1.8) * 0.8,
            "health": 300,
            "points": 600,
        },
        "size": 1.8,
        "speed": 30,
        # Each bay launches its Hornet every `launchInterval`, the bays one by one in turn (one
        # Hornet every `launchInterval` / 4); the first after `firstLaunch`.
        "launchInterval": 3,
        "firstLaunch": 1.2,
        # The landing bays on its right side (mirrored on the left), from its centre: out to the
        # side and up the screen, in px; a docked Hornet's centre, nose out. The model digs its
        # bays there (ENM-CARRIER-02).
        "ports": [
            [13, 12],
            [13, -4],
        ],
        # How far out to the side a Hornet flies from its bay before its pause, in px.
        "launchExit": 30,
        # It stops launching below this height, too close to the player (ENM-CARRIER-09).
        "lastLaunchFraction": 0.3,
        "xRange": [0.3, 0.7],
    },
    # The pods a destroyed Splitter breaks into: small Hornets (ENM-SPLITTER-08; health and
    # points: ENM-SPLITTER-09).
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
})
