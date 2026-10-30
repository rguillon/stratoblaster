"""Look of the player shots (P03-R01..R03)

Linear RGB, 0..1. Sizes in logical pixels unless noted; durations in seconds. Shots are drawn with
additive blending: black is transparent.
"""

from game.config.record import record

SHOT_LOOK = record(
    {
        # Minigun tracer (phase 5 review, was a green blob): a long thin streak, white-hot at its
        # head, cooling to cyan then deep blue along its tail (phase 14, P14-R02: was orange then
        # red, the enemy shots' colours).
        "bullet": {
            # Phase 14: a little wider (was 3.4), so it still shows toned down (P14-R06).
            "width": 4.2,
            # Length of the streak behind the bullet; a new one grows to it from the muzzle.
            "length": 34,
            # Across the streak, centre line to edge.
            "colors": [
                [1, 1, 1],
                [0.3, 0.8, 1],
                [0.04, 0.25, 0.5],
                [0, 0, 0],
            ],
            # Along the streak, from its rounded tip (0.08 ahead of the bullet) back to the tail end
            # (-1): how far back, and what the colours are multiplied by there.
            "rows": [
                {"at": 0.08, "tint": [0, 0, 0]},
                {"at": 0, "tint": [1, 1, 1]},
                {"at": -0.2, "tint": [0.85, 0.95, 1]},
                {"at": -0.6, "tint": [0.35, 0.6, 0.75]},
                {"at": -1, "tint": [0, 0, 0]},
            ],
            # Width flicker of each tracer (+- fraction) and its rate, rad/s.
            "flicker": 0.18,
            "flickerRate": 90,
            # Distance behind the playfield plane, so the ship (at Z = 0) is drawn over the tracers
            # leaving from inside it (reviewer, 2026-10-26).
            "depth": 8,
        },
        "laser": {
            # Visual width relative to the beam's hit width (the glow spills around the core).
            "glowWidth": 1.8,
            # Centre line to edge.
            "colors": [
                [0.55, 0.8, 1],
                [0.12, 0.42, 1],
                [0.02, 0.1, 0.55],
                [0, 0, 0],
            ],
            # Width flicker (+- fraction) and its frequency, Hz.
            "flicker": 0.12,
            "flickerHz": 23,
            "particles": {
                "count": 48,
                # Speed along the beam, px/s.
                "speed": [500, 900],
                "radius": [1.2, 2.6],
                # Sideways spread, as a fraction of the local beam width.
                "spread": 0.9,
                "colors": [
                    [0.5, 0.8, 1],
                    [0.1, 0.35, 0.9],
                    [0, 0, 0],
                ],
                "seed": 3,
            },
            # Glow at the base of the beam (review feedback): its radius is `radius` times
            # (`baseScale` + beam width / `widthDivisor`), pulsing by +- `pulse`, stretched along
            # the beam.
            "muzzle": {
                "radius": 12,
                "baseScale": 0.6,
                "widthDivisor": 12,
                "stretch": 1.3,
                "pulse": 0.15,
                "pulseHz": [9, 17],
                # Round and smooth (phase 3 review: it looked polygonal): 24 sides and 6 rings
                # following a soft, roughly exponential falloff; 24 x 11 = 264 triangles for the
                # one glow.
                "segments": 24,
                "colors": [
                    [0.8, 0.95, 1],
                    [0.55, 0.8, 1],
                    [0.3, 0.6, 1],
                    [0.15, 0.38, 0.9],
                    [0.06, 0.18, 0.55],
                    [0.02, 0.06, 0.22],
                    [0, 0, 0],
                ],
            },
            # Glow where the beam touches a target.
            "contact": {
                "radius": 9,
                "colors": [
                    [0.5, 0.75, 1],
                    [0.1, 0.35, 0.9],
                    [0, 0, 0],
                ],
            },
        },
        "missile": {
            # Model units (scaled by the player ship scale): body length and radius.
            # Phase 5 review: about 30 % bigger (1.7 / 0.16 / 0.32 before), with a lighter body.
            "length": 2.2,
            "radius": 0.2,
            "finSpan": 0.4,
            "body": [0.78, 0.8, 0.85],
            "tip": [0.3, 0.85, 1],
            "flame": {"length": 1.6, "diameter": 0.36, "puffDiameter": 0.28, "sides": 6},
            # Phase 5 review, to stand out on any ground: a bright motor flare at the nozzle (radius
            # in px, +- flicker at `flickerRate` rad/s) and a glowing exhaust trail behind it (px),
            # growing from the launch like a tracer.
            "flare": {
                "radius": 7,
                "flicker": 0.25,
                "flickerRate": 70,
                "colors": [
                    [1, 1, 1],
                    [0.6, 0.85, 1],
                    [0.15, 0.35, 0.8],
                    [0, 0, 0],
                ],
                "segments": 10,
            },
            "trail": {
                "width": 4,
                "length": 46,
                "colors": [
                    [0.85, 0.95, 1],
                    [0.35, 0.6, 1],
                    [0, 0, 0],
                ],
                "rows": [
                    {"at": 0, "tint": [1, 1, 1]},
                    {"at": -0.3, "tint": [0.6, 0.6, 0.7]},
                    {"at": -1, "tint": [0, 0, 0]},
                ],
            },
            # Distance behind the playfield plane (away from the camera), so the ship (at Z = 0) is
            # drawn over missiles leaving its centre (phase 3 review).
            "depth": 20,
        },
        "impact": {
            # Bullet hit: a burst of sparkling metal sparks (phase 3 review) sprayed back from the
            # hit, slowing down, twinkling and shrinking away. Speeds in px/s, durations in s,
            # angles in degrees around "straight back" (bullets fly up, so the sparks spray down
            # and sideways).
            "bullet": {
                "count": 14,
                "speed": [120, 380],
                "spreadDeg": 80,
                # Speed lost per second, as a rate: v *= exp(-drag x dt).
                "drag": 7,
                "life": [0.18, 0.4],
                # Streak length (along its motion) and width, at the start of its life.
                "length": [8, 16],
                "width": 2.4,
                # Brightness flicker of each spark (+- fraction) and its frequency range.
                "twinkle": 0.45,
                "twinkleHz": [18, 34],
                # Centre to edge: white-hot, ice blue (phase 14: was gold), black (transparent).
                "colors": [
                    [0.95, 1, 1],
                    [0.3, 0.75, 1],
                    [0, 0, 0],
                ],
                # A diamond: 4 x (2 x 2 - 1) = 12 triangles per spark (40 before the phase 3
                # review).
                "segments": 4,
                "seed": 11,
            },
            # Missile explosion; its radius is the blast radius times this factor.
            "missile": {
                "radiusFactor": 1.6,
                "duration": 0.3,
                # Phase 14 (P14-R02): in the player's cyan, not the enemy shots' orange.
                "colors": [
                    [0.75, 0.95, 1],
                    [0.2, 0.6, 1],
                    [0.04, 0.18, 0.45],
                    [0, 0, 0],
                ],
            },
            "segments": 16,
        },
    }
)
