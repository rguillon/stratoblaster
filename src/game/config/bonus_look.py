# Copyright (c) 2026 Renaud Guillon
"""Look of the bonuses.

Weapon bonuses (GFX-FX-11; phase 6 review): a hexagon badge with chevrons pointing up (a level
up), swinging from side to side over a pulsing halo; a ring flashes out where the ship picks one up
(GFX-FX-13). GFX-FX-12: life bonuses are a heart, bomb bonuses a ball marked B, heal bonuses a
plus sign (GAME-BONUS-11), so each kind reads by its shape. Phase 14 (GFX-ART-07): all in the
pickups' family, violet since D-231 (reviewer, 2026-11-01: the enemies took the yellow and green;
were an acid green badge, a mint heart and a green ball, and before phase 14 yellow, pink and
orange).

Linear RGB, 0..1; sizes in logical pixels; times in seconds.
"""

from game.config.record import record

BONUS_LOOK = record({
    # Radius of the badge (corner of its hexagon).
    "size": 11,
    # In front of the ships and the explosions (towards the camera, -Z).
    "depth": -4,
    # Below full strength: the playfield's glow would wash them out to white.
    # Phase 14 (GFX-READ-06, reviewer): every bonus in the pickups' family, the kinds told apart
    # by their shapes (D-231: a blue violet, not pink; was acid green, and acid yellow with cyan
    # chevrons before).
    "frame": [0.55, 0.3, 1],
    "face": [0.06, 0.04, 0.1],
    "chevrons": [0.75, 0.6, 1],
    # Inner edge of the frame, as a share of the size.
    "frameInset": 0.78,
    # It swings around its upright axis, up to `amplitude` radians each way, `hz` times a
    # second (a whole turn would show it edge on half the time).
    "swing": {"amplitude": 0.9, "hz": 0.7},
    "halo": {
        "colors": [
            [0.28, 0.14, 0.52],
            [0.12, 0.06, 0.23],
            [0.035, 0.015, 0.06],
            [0, 0, 0],
        ],
        # Radius, as a multiple of the badge size.
        "size": 1.7,
        # It swells and shrinks by this share, this many times a second.
        "pulse": 0.2,
        "pulseHz": 2.5,
        "segments": 20,
    },
    "flash": {"size": 4, "life": 0.35, "color": [0.7, 0.5, 1], "segments": 32},
    # A life bonus (GFX-FX-12): the heart's rim, the heart, how far in the heart is, its halo.
    "life": {
        "rim": [0.4, 0.15, 0.85],
        "heart": [0.72, 0.5, 1],
        "inset": 0.72,
        "halo": [
            [0.22, 0.09, 0.46],
            [0.1, 0.04, 0.2],
            [0.025, 0.01, 0.05],
            [0, 0, 0],
        ],
    },
    # A heal bonus (GFX-FX-12, GAME-BONUS-11): the plus sign's rim, the plus sign, how far in it is,
    # its halo.
    "heal": {
        "rim": [0.4, 0.15, 0.85],
        "cross": [0.85, 0.75, 1],
        "inset": 0.7,
        "halo": [
            [0.24, 0.12, 0.5],
            [0.11, 0.05, 0.22],
            [0.03, 0.012, 0.06],
            [0, 0, 0],
        ],
    },
    # A bomb bonus (GFX-FX-12): its shell, highlight, letter and halo.
    "bomb": {
        "shell": [0.45, 0.2, 0.95],
        "highlight": [0.8, 0.65, 1],
        "letter": [0.05, 0.02, 0.01],
        "halo": [
            [0.25, 0.1, 0.5],
            [0.11, 0.045, 0.22],
            [0.03, 0.012, 0.06],
            [0, 0, 0],
        ],
    },
})
