# Copyright (c) 2026 Renaud Guillon
"""The sample game's looks: the playfield camera and the window atlas.

They take the values of a game that uses the engine: a screen of 480 x 640, a tilted camera, a
512-pixel atlas of 8-pixel cells with four window styles and two door bands of two columns.
"""

from fixtures.sample_game.record import record

PLAYFIELD_CAMERA = record({
    "tiltDeg": 35,
    "fovDeg": 40,
    "flightAltitude": 320,
    "groundScale": 2,
})

WINDOW_ATLAS = record({
    "size": 512,
    "cell": 8,
    "styles": [
        {"window": [2, 2, 6, 6], "lit": 0.18},
        {"window": [0, 3, 8, 6], "lit": 0.2},
        {"window": [3, 1, 5, 7], "lit": 0.15},
        {"window": [1, 1, 7, 7], "lit": 0.22},
    ],
    "doors": [
        {"window": [2, 0, 6, 7], "lit": 0.5},
        {"window": [0, 0, 8, 6], "lit": 0.45},
    ],
    "doorColumns": 2,
    "colors": [
        [1, 0.82, 0.55],
        [1, 0.72, 0.4],
        [1, 0.9, 0.72],
        [0.92, 0.95, 1],
        [0.65, 0.8, 1],
    ],
    "brightness": [0.45, 1],
    "blinds": 0.25,
    "dark": [0.01, 0.01, 0.015],
    "glass": [0.25, 0.25, 0.25],
    "halo": 0.3,
    "seed": 4242,
})
