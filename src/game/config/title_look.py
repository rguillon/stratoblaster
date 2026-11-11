# Copyright (c) 2026 Renaud Guillon
"""The neon trench behind the menus (UI-TITLE-07, D-325).

UI-TITLE-08: neon blue/green (D-198). The balanced ship races down a dark trench towards the
camera: blue-grey walls of uneven panels with cyan, green and blue slots, a neon strip along their
feet, lit ribs across the floor, a dashed guide line, haze, a deep blue glow at the far end, and
speed streaks rushing past. Linear RGB, 0..1. Distances in world units; the camera looks towards
-Z, the ship's nose towards +Z; heights in gradient stops go from -1 (bottom) to 1 (top).
"""

from game.config.record import record

NEON = [
    [0.05, 0.9, 1],
    [0.15, 1, 0.5],
    [0.1, 0.4, 1],
    [0.55, 1, 0.85],
]

WINDOW_COLORS = [
    [0.05, 0.85, 1],
    [0.15, 0.95, 0.45],
    [0.15, 0.4, 1],
]

STREAK_COLORS = [
    [0.6, 0.95, 1],
    [0.1, 0.85, 1],
    [0.85, 1, 1],
]

TITLE_LOOK = record({
    # Seed of the trench and streak generators: the same trench on every run.
    "seed": 2077,
    # Ahead of the ship, a little above it, looking back down the trench (a frontal camera).
    "camera": {"position": [0, 2.4, 10], "target": [0, 0, -30], "fov": 0.8},
    # Haze colour; also the clear colour, so the trench melts into the distance.
    "horizon": [0.01, 0.05, 0.1],
    "fog": {"start": 20, "end": 140},
    # The glow at the far end of the trench; not fogged.
    "sky": {
        "z": -200,
        "width": 400,
        "height": 300,
        "centerY": 40,
        # Deep blue glow low down, through teal, to black higher up.
        "stops": [
            {"at": -1, "color": [0.01, 0.12, 0.3]},
            {"at": -0.7, "color": [0.01, 0.13, 0.18]},
            {"at": -0.2, "color": [0.004, 0.03, 0.06]},
            {"at": 1, "color": [0.001, 0.004, 0.012]},
        ],
    },
    "trench": {
        # One stretch, from z = 0 back to z = -length; two stretches end to end.
        "length": 160,
        # `title_trench_speed`, in units per second, away from the camera.
        "speed": 60,
        # Where the first stretch starts: past the camera, so the trench always reaches it.
        "startZ": 24,
        "halfWidth": 5,
        "floorY": -3,
        "wallHeight": 16,
        # Wall panels: their length along the trench, and how far each stands out of the wall.
        "panelLength": [3, 9],
        "panelDepth": [0, 1.4],
        "colors": {
            "floor": [0.006, 0.02, 0.03],
            "wall": [0.03, 0.07, 0.1],
            "wallAlt": [0.05, 0.11, 0.15],
            "edge": [0.015, 0.04, 0.06],
        },
        # Lit slots on the panels.
        "slots": {
            "chance": 0.7,
            "width": [0.8, 3],
            "height": [0.15, 0.4],
            "y": [0.5, 12],
            "brightness": [0.4, 0.9],
            "colors": WINDOW_COLORS,
        },
        # The neon strip along the foot of each wall.
        "strip": {"y": [0.3, 0.45], "color": NEON[0]},
        # Lit ribs across the floor, every `every` units.
        "ribs": {"every": 10, "width": 0.25, "color": [0.05, 0.6, 0.75]},
        # The dashed guide line down the middle of the floor.
        "guide": {"halfWidth": 0.08, "dash": 3, "period": 8, "color": NEON[1]},
    },
    # Speed streaks rushing past: thin quads along the trench, round its axis, facing it.
    "streaks": {
        "count": 220,
        # One stretch of streaks, from z = 0 back to z = -length; two end to end.
        "length": 60,
        "startZ": 16,
        # `title_streaks` speed, in units per second, away from the camera: faster than the trench.
        "speed": 160,
        # Round the camera's line of sight (x = 0, y = axisY), between these distances from it: far
        # enough that none passes right by the camera lens.
        "axisY": 2.4,
        "radius": [3, 5.2],
        "size": [2, 7],
        "width": 0.03,
        "brightness": [0.4, 0.85],
        "colors": STREAK_COLORS,
    },
    "ship": {
        "position": [0, -0.5, 0],
        # `title_ship_sway`: side to side, banking into each turn.
        "swayAmplitude": 0.8,
        "swayHz": 0.18,
        "bankRad": 0.35,
        # `title_ship_float`: a gentle up-and-down.
        "bobAmplitude": 0.2,
        "bobHz": 0.5,
    },
    # Lit from the camera's side, so the ship's nose and wings catch the light.
    "lights": {"ambient": 0.7, "key": 2, "keyDirection": [-0.3, -1, -0.6]},
    # Brightness of the neon meshes; the glow layer and tone mapping wash them out above this
    # (UI-TITLE-10).
    "neonIntensity": 0.45,
})
