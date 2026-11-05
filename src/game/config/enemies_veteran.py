# Copyright (c) 2026 Renaud Guillon
"""Tunables of the five veteran kinds (ENM-06; each kind's file in specs/enemies/).

In the units of `enemies.py`: logical pixels, px/s, seconds, degrees; `...Fraction` heights are
fractions of the playfield height from its bottom. `muzzles` as in `enemies.py` (offsets from the
centre facing down the screen, X right, Y up, and heights).
"""

from game.config.enemies import ENEMY_UNIT, fan_barrels
from game.config.enemy_look import ENEMY_LOOK
from game.config.record import record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def radius(size: float) -> float:
    """Hit radius of an enemy `size` L across, about as big as the model (ENM-11, as enemies.py)."""
    return (size * ENEMY_UNIT * 0.85) / 2


def bullet(style: str, speed: float, size: float = 4) -> Any:
    """Return a glowing bullet of a style of `enemy_look`."""
    return record({"speed": speed, "radius": size, "style": style})


# The Phantom's five guns (ENM-PHANTOM-03), fanned 12 degrees apart, `PHANTOM_GUN_GAP` apart
# across: each tip about 5 px ahead of the wing's swept leading edge there (middle, then further
# out), at a height inside the wing.
PHANTOM_GUN_GAP = 3.2
PHANTOM_GUN_TIPS = [18.4, 15.2, 11.9]
PHANTOM_GUN_HEIGHT = -0.6


def phantom_barrels() -> list[list[float]]:
    """Return the Phantom's barrels, `[x, y, height, angle]` (see `fan_barrels`)."""
    barrels: list[list[float]] = []
    for i in range(5):
        k = i - 2
        tip = PHANTOM_GUN_TIPS[abs(k)]
        barrels.append([-k * PHANTOM_GUN_GAP, -tip, PHANTOM_GUN_HEIGHT, k * 12])
    return barrels


VETERAN_CONFIG = record({
    # ENM-WASP-11: health, points and hit circle.
    "wasp": {
        "stats": {"model": "wasp", "radius": radius(0.6), "health": 30, "points": 150},
        "size": 0.6,
        # A swarm of drones.
        "groupSize": 5,
        # Distance between two Wasps of a group, side by side.
        "groupSpacing": 34,
        "entrySpeed": 240,
        # Height where they stop before the dive.
        "stopFraction": 0.72,
        "entryBrake": 480,
        "pause": 0.4,
        "diveAcceleration": 1000,
        "diveMaxSpeed": 600,
        # The fan fired at the end of the pause: 3 bullets 12 degrees apart, the middle one
        # aimed.
        "fanCount": 3,
        "fanSpacing": 12,
        "bullet": bullet("orange", 220),
        # The guns of the sensor pod at its nose.
        "muzzles": fan_barrels(3, 12, 1.2, -10.4, 0.8),
        # Range of X of the group's middle Wasp, as fractions of the width.
        "xRange": [0.25, 0.75],
    },
    # ENM-MORTAR-10: health, points and hit circle.
    "mortar": {
        "stats": {"model": "mortar", "radius": radius(1.2) * 0.8, "health": 120, "points": 350},
        "size": 1.2,
        "speed": 40,
        "fireInterval": 3.5,
        "firstShot": 1,
        # A slow, heavy homing missile (ENM-MORTAR-08) that can be shot down; its fuse is out
        # 2.5 s after launch and it bursts into a ring of 10 bullets (ENM-MORTAR-09).
        "missile": {
            "speed": 90,
            "turnRateDeg": 55,
            "homingSeconds": 2.2,
            "radius": 8,
            "health": 20,
            "style": "mortar",
            "burst": {"after": 2.5, "count": 10, "bullet": bullet("green", 130)},
        },
        # The mouth of the short, wide launcher tube on its raised mount.
        "muzzles": [[0, -12.5, 7]],
        "xRange": [0.2, 0.8],
    },
    # ENM-PHANTOM-13: health, points and hit circle.
    "phantom": {
        "stats": {"model": "phantom", "radius": radius(1) * 0.8, "health": 90, "points": 450},
        "size": 1,
        "entrySpeed": 150,
        # Between its places it speeds up to `cruiseSpeed` at `acceleration`, its nose turning
        # along its way at up to `turnDeg` per second, and brakes into each place at `brake`.
        "cruiseSpeed": 170,
        "acceleration": 260,
        "brake": 300,
        "turnDeg": 240,
        # Where it flies to and fires from: X across the width, heights in the upper half.
        "placeX": [0.15, 0.85],
        "placeY": [0.6, 0.82],
        # Each place at least this far from the one before.
        "moveDistance": 110,
        # It fires from this many places (ENM-PHANTOM-09); after the last it dives.
        "stops": 2,
        # How long it takes to point at the player before it fires, and how long it holds after.
        "aimTime": 0.5,
        "hold": 0.4,
        # The dive (ENM-PHANTOM-11): the pause turning its nose to the player, then the
        # acceleration and the top speed.
        "pause": 0.5,
        "diveAcceleration": 900,
        "diveMaxSpeed": 560,
        # The spread fired at each place: 5 bullets 12 degrees apart, centred on the player.
        "spreadCount": 5,
        "spreadSpacing": 12,
        "bullet": bullet("purple", 200),
        # The guns along the front of its wing, spread wide, sunk in it: their ends stick out
        # past the nose and the leading edges.
        "muzzles": phantom_barrels(),
        "xRange": [0.25, 0.75],
    },
})

# Neon colours of the veteran-era kinds: their tier's (ENM-49), as `ENEMY_LOOK.neon`.
VETERAN_NEON = ENEMY_LOOK.neon
