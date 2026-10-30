"""Look of the bonuses

Weapon bonuses (phase 6 review): a hexagon badge with chevrons pointing up (a level up), swinging
from side to side over a pulsing halo; a ring flashes out where the ship picks one up. P11-R07: life
bonuses are a heart, bomb bonuses a ball marked B, so each kind reads by its shape. Phase 14
(P14-R02): all in the pickups' green family (acid green badge, mint heart, green ball; were yellow,
pink and orange).

Linear RGB, 0..1; sizes in logical pixels; times in seconds.
"""

from game.config.record import record

BONUS_LOOK = record(
    {
        # Radius of the badge (corner of its hexagon).
        "size": 11,
        # In front of the ships and the explosions (towards the camera, -Z).
        "depth": -4,
        # Below full strength: the playfield's glow would wash them out to white.
        # Phase 14 (P14-R02, reviewer): every bonus in the pickups' green family, the kinds told
        # apart by their shapes (was acid yellow with cyan chevrons).
        "frame": [0.45, 0.85, 0.05],
        "face": [0.06, 0.04, 0.1],
        "chevrons": [0.05, 0.75, 0.35],
        # Inner edge of the frame, as a share of the size.
        "frameInset": 0.78,
        # It swings around its upright axis, up to `amplitude` radians each way, `hz` times a
        # second (a whole turn would show it edge on half the time).
        "swing": {"amplitude": 0.9, "hz": 0.7},
        "halo": {
            "colors": [
                [0.28, 0.5, 0.04],
                [0.12, 0.22, 0.02],
                [0.03, 0.06, 0.01],
                [0, 0, 0],
            ],
            # Radius, as a multiple of the badge size.
            "size": 1.7,
            # It swells and shrinks by this share, this many times a second.
            "pulse": 0.2,
            "pulseHz": 2.5,
            "segments": 20,
        },
        "flash": {"size": 4, "life": 0.35, "color": [0.35, 1, 0.55], "segments": 32},
        # A life bonus (P11-R07): the heart's rim, the heart, how far in the heart is, its halo.
        "life": {
            "rim": [0.1, 0.7, 0.3],
            "heart": [0.55, 1, 0.6],
            "inset": 0.72,
            "halo": [
                [0.08, 0.45, 0.2],
                [0.03, 0.2, 0.09],
                [0.01, 0.05, 0.02],
                [0, 0, 0],
            ],
        },
        # A bomb bonus (P11-R07): its shell, highlight, letter and halo.
        "bomb": {
            "shell": [0.2, 0.75, 0.1],
            "highlight": [0.7, 1, 0.45],
            "letter": [0.05, 0.02, 0.01],
            "halo": [
                [0.2, 0.48, 0.06],
                [0.09, 0.22, 0.03],
                [0.02, 0.06, 0.01],
                [0, 0, 0],
            ],
        },
    }
)
