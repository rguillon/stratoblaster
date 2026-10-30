"""Look of a bomb going off (P11-R05)

A cyan shockwave ring growing from the ship until it covers the playfield, fading as it goes, and a
short warm flash at the ship. One bomb at a time and each lasting 1 s, there is never more than one
flash a second (below the 3 a second limit). Linear RGB, 0..1; sizes in logical pixels; times in
seconds.
"""

from game.config.record import record

BOMB_LOOK = record(
    {
        # In front of the ships and the explosions (towards the camera, -Z).
        "depth": -5,
        "wave": {
            # Radius it reaches as the bomb ends: past the corners of the 480 x 640 playfield.
            "radius": 820,
            # Rings from the centre out: black (nothing, added on) inside, a bright rim.
            "colors": [
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
                [0.05, 0.25, 0.3],
                [0.3, 0.9, 1],
                [0, 0, 0],
            ],
            "segments": 48,
        },
        "flash": {
            # Seconds it fades over, and its radius.
            "seconds": 0.3,
            "radius": 320,
            # Phase 14 (P14-R07): dimmer (was 0.7 at its heart), so the ship and the enemy bullets
            # that survive the bomb stay visible through it; the bullets are drawn over it.
            "colors": [
                [0.4, 0.34, 0.22],
                [0.22, 0.17, 0.1],
                [0.07, 0.05, 0.02],
                [0, 0, 0],
            ],
            "segments": 32,
        },
    }
)
