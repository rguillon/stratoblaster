# Copyright (c) 2026 Renaud Guillon
"""Tunables of the five veteran kinds (ENM-06; each kind's file in specs/enemies/).

In the units of `enemies.py`: logical pixels, px/s, seconds, degrees; `...Fraction` heights are
fractions of the playfield height from its bottom. `muzzles` as in `enemies.py` (offsets from the
centre facing down the screen, X right, Y up, and heights).
"""

import math

from game.config.enemies import ENEMY_UNIT
from game.config.record import merge, record

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


# The Mantis's shoulders (the arms' joints), either side of its head, from its centre.
MANTIS_SHOULDER = [8, -5]
# The Mantis's arms: from the shoulder to the blade's tip, and turned out at rest.
MANTIS_ARM = record({"length": 22, "outDeg": 14})


def mantis_tip(s: float, reach: float) -> list[float]:
    """Return the tip of the Mantis's arm on the side `s` at rest, from its centre.

    `s` is 1 for the right side, -1 for the left.
    """
    a = (MANTIS_ARM.outDeg * math.pi) / 180
    return [
        s * (MANTIS_SHOULDER[0] + math.sin(a) * reach),
        MANTIS_SHOULDER[1] - math.cos(a) * reach,
    ]


def mantis_muzzles(s: float) -> list[list[float]]:
    """Return the pair of muzzles at the tip of the Mantis's arm on the side `s`, across the blade.

    ENM-MANTIS-10: the arm's pairs of shots leave from there.
    """
    a = (MANTIS_ARM.outDeg * math.pi) / 180
    tip = mantis_tip(s, MANTIS_ARM.length)
    x = tip[0]
    y = tip[1]
    # 1.6 px either side of the blade, square to it (outwards: `s` cos a across, sin a up).
    dx = s * math.cos(a) * 1.6
    dy = math.sin(a) * 1.6
    return [
        [x - dx, y - dy, 1.2],
        [x + dx, y + dy, 1.2],
    ]


VETERAN_CONFIG = record({
    # ENM-WASP-11: health, points and hit circle.
    "wasp": {
        "stats": {"model": "wasp", "radius": radius(0.6), "health": 30, "points": 150},
        "size": 0.6,
        "groupSize": 3,
        # Distance between two Wasps of a group, side by side.
        "groupSpacing": 42,
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
        # The gun between its mandibles.
        "muzzles": [[0, -10.4, 0.8]],
        # Range of X of the group's middle Wasp, as fractions of the width.
        "xRange": [0.25, 0.75],
    },
    # ENM-MORTAR-10: health, points and hit circle.
    "mortar": {
        "stats": {"model": "mortar", "radius": radius(1.2) * 0.8, "health": 140, "points": 400},
        "size": 1.2,
        "speed": 40,
        "fireInterval": 2.5,
        "firstShot": 1,
        # A big, slow shell aimed at the player (ENM-MORTAR-08), bursting into a ring of 8
        # bullets after 1.2 s (ENM-MORTAR-09); drawn as a bigger ball of plasma (GFX-SHOT-14).
        "shell": merge(
            bullet("green", 110, 7),
            {"burst": {"after": 1.2, "count": 8, "bullet": bullet("green", 150)}},
        ),
        # The mouth of the short, wide barrel on its raised mount.
        "muzzles": [[0, -12.5, 7]],
        "xRange": [0.2, 0.8],
    },
    # ENM-MANTIS-13: health, points and hit circle.
    "mantis": {
        "stats": {"model": "mantis", "radius": radius(1.4) * 0.5, "health": 160, "points": 500},
        "size": 1.4,
        "entrySpeed": 120,
        "brakeDistance": 70,
        # It stops at a random height between these (the upper half).
        "stopRange": [0.62, 0.76],
        "stay": 6,
        "exitSpeed": 100,
        "shoulder": MANTIS_SHOULDER,
        "arm": merge(
            MANTIS_ARM,
            {
                "health": 50,
                # Hit circle, on the middle of the blade.
                "radius": 6,
                "centre": 13,
                # Each arm swings out and back every `period` s, a quarter period after the
                # other (ENM-MANTIS-09).
                "swing": {"amplitudeDeg": 24, "period": 2.4},
                "fireInterval": 1.2,
                # Each arm's pair of bullets, straight along the blade (ENM-MANTIS-10).
                "bullet": bullet("green", 210),
                # The tip of the arm's blade: the pair leaves from either side of it.
                "muzzles": {"left": mantis_muzzles(-1), "right": mantis_muzzles(1)},
            },
        ),
        "head": {
            "fireInterval": 2,
            "firstShot": 1,
            "bullet": bullet("green", 200),
            # The gun on its narrow head.
            "muzzles": [[0, -14.6, 1.4]],
        },
        "xRange": [0.25, 0.75],
    },
    # ENM-PHANTOM-13: health, points and hit circle.
    "phantom": {
        "stats": {"model": "phantom", "radius": radius(1) * 0.8, "health": 90, "points": 450},
        "size": 1,
        "entrySpeed": 150,
        "brakeDistance": 60,
        # Where it moves to and reappears: X across the width, heights in the upper half.
        "placeX": [0.15, 0.85],
        "placeY": [0.6, 0.82],
        # Each place at least this far from the one before.
        "jumpDistance": 110,
        "fade": 0.4,
        "hidden": 0.8,
        "jumps": 3,
        # How long it stays in view before it fades out again (or leaves).
        "hold": 0.6,
        # Shots go through it while it is less visible than this (ENM-PHANTOM-12).
        "solidOpacity": 0.5,
        "exitSpeed": 170,
        # The spread fired as it reappears: 5 bullets 12 degrees apart, centred on the player.
        "spreadCount": 5,
        "spreadSpacing": 12,
        "bullet": bullet("purple", 200),
        # The gun under its nose.
        "muzzles": [[0, -14.6, 0.6]],
        "xRange": [0.25, 0.75],
    },
    # ENM-MINELAYER-10: health, points and hit circle.
    "minelayer": {
        "stats": {
            "model": "minelayer",
            "radius": radius(1.3) * 0.6,
            "health": 120,
            "points": 400,
        },
        "size": 1.3,
        "speed": 110,
        # Height of its pass, in the top half.
        "heightFraction": 0.74,
        # Its pass is never lower than this, whatever the wave's entry.
        "lowestFraction": 0.55,
        "dropInterval": 0.8,
        "firstDrop": 0.4,
        # A mine: a slow bullet drifting down that bursts into a ring of 6 after 1.5 s
        # (ENM-MINELAYER-09).
        "mine": merge(
            bullet("red", 45, 6),
            {"burst": {"after": 1.5, "count": 6, "bullet": bullet("red", 140)}},
        ),
        # The hatches of the mine rack along its belly, dropping in turn.
        "muzzles": [
            [0, -8, -3],
            [0, 0, -3],
            [0, 8, -3],
        ],
    },
})

# Neon colours of the veteran kinds, one each (ENM-06; drawn yellow or green, ENM-38). Linear RGB.
VETERAN_NEON = record({
    # ENM-WASP-03: yellow.
    "wasp": [1, 0.85, 0.05],
    # ENM-MORTAR-03: bright yellow (drawn yellow, keeping its brightness: as bright as the other
    # yellow kinds, whose largest channel is 1; was olive green, drawn dark).
    "mortar": [1, 0.92, 0.1],
    # ENM-MANTIS-03: lime (drawn yellow).
    "mantis": [0.6, 1, 0.1],
    # ENM-PHANTOM-03: pale violet (drawn green).
    "phantom": [0.75, 0.6, 1],
    # ENM-MINELAYER-03: red-orange (drawn yellow).
    "minelayer": [1, 0.3, 0.05],
})
