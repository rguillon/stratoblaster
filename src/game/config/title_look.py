# Copyright (c) 2026 Renaud Guillon
"""Synthwave dusk behind the menus (UI-TITLE-07).

UI-TITLE-08: synthwave dusk since D-323 (blue/green D-198, darksynth magenta before). A dim magenta
dusk behind a black skyline, a dark violet street of towers with pink, violet and cyan windows,
signs and roof trims, haze and rain (D-012). Linear RGB, 0..1. Distances in world units; heights
in gradient stops go from -1 (bottom) to 1 (top).
"""

from game.config.record import record

NEON = [
    [1, 0.25, 0.6],
    [0.2, 0.85, 1],
    [0.65, 0.3, 1],
    [1, 0.55, 0.2],
]

WINDOW_COLORS = [
    [1, 0.3, 0.65],
    [0.7, 0.4, 1],
    [0.3, 0.85, 1],
]

TITLE_LOOK = record({
    # Seed of the city generator: the same city on every run.
    "seed": 2077,
    "camera": {"position": [0, 4, -8], "target": [0, 5.5, 40], "fov": 0.8},
    # Haze colour; also the clear colour, so the street melts into the distance.
    "horizon": [0.05, 0.015, 0.08],
    "fog": {"start": 30, "end": 190},
    "sky": {
        "z": 340,
        "width": 900,
        "height": 400,
        "centerY": 150,
        # Dim magenta dusk near the horizon, through violet, to near black higher up.
        "stops": [
            {"at": -1, "color": [0.32, 0.04, 0.22]},
            {"at": -0.7, "color": [0.18, 0.03, 0.2]},
            {"at": -0.2, "color": [0.04, 0.01, 0.07]},
            {"at": 1, "color": [0.006, 0.003, 0.014]},
        ],
    },
    # Distant towers, flat, in front of the sky; not fogged.
    "skyline": {
        "z": 300,
        "y": -10,
        "halfWidth": 420,
        "width": [10, 30],
        "height": [40, 150],
        "color": [0.016, 0.008, 0.028],
        "windows": {
            "cellWidth": 3,
            "cellHeight": 4,
            "width": 1.4,
            "height": 1.8,
            "groundFloor": 12,
            "litChance": 0.12,
            "brightness": [0.35, 0.7],
            "colors": WINDOW_COLORS,
        },
    },
    "city": {
        # Length of one city chunk; two chunks scroll end to end.
        "length": 200,
        "streetHalfWidth": 9,
        # `title_city_scroll_speed`, in units per second.
        "scrollSpeed": 8,
        "rows": [
            {
                "facadeOffset": 0,
                "width": [6, 14],
                "gap": [1, 3],
                "depth": [8, 16],
                "height": [14, 55],
                "signs": True,
            },
            {
                "facadeOffset": 22,
                "width": [10, 22],
                "gap": [2, 6],
                "depth": [10, 20],
                "height": [45, 115],
                "signs": False,
            },
        ],
        "colors": {
            "wall": [0.04, 0.02, 0.06],
            "facade": [0.06, 0.03, 0.085],
            "roof": [0.025, 0.012, 0.04],
        },
        "street": {
            "halfWidth": 80,
            "color": [0.018, 0.008, 0.028],
            "laneX": [-3, 3],
            "dash": 3,
            "dashPeriod": 8,
            "lineWidth": 0.15,
            "lineColor": [0.6, 0.1, 0.4],
        },
        "windows": {
            "cellWidth": 2.2,
            "cellHeight": 2.8,
            "width": 1.1,
            "height": 1.5,
            "groundFloor": 3,
            "litChance": 0.3,
            "brightness": [0.3, 0.75],
            "colors": WINDOW_COLORS,
        },
        "neonColors": NEON,
        "signs": {
            "chance": 0.5,
            "width": [1.4, 2.6],
            "height": [5, 12],
            "baseHeight": [3, 16],
            "panel": [0.03, 0.012, 0.045],
            "lines": 3,
        },
        "trim": {"chance": 0.35, "height": 0.3},
    },
    "rain": {
        "count": 260,
        "halfWidth": 30,
        "height": 30,
        # Bottom of the rain box.
        "y": -2,
        "z": [0, 60],
        "length": [0.8, 1.6],
        "width": 0.04,
        "color": [0.28, 0.16, 0.4],
        # Fall speed, in units per second.
        "speed": 30,
    },
    "ship": {
        "position": [0, 1.6, 8],
        # `title_ship_rotation_speed`.
        "rotationSpeedRadPerSec": 0.3,
        # Gentle up-and-down float.
        "bobAmplitude": 0.25,
        "bobHz": 0.35,
    },
    "lights": {"ambient": 0.7, "key": 2, "keyDirection": [-0.3, -1, 0.5]},
    # Brightness of the neon meshes; the glow layer and tone mapping wash them out above this
    # (UI-TITLE-10).
    "neonIntensity": 0.45,
})
