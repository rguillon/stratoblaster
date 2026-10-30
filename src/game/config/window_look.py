"""The building windows (D-210): the atlas they are painted into (see
`render/scenery/window_atlas.py`) and how big a window cell is on a wall.

Linear RGB, 0..1; sizes in pixels for the atlas, in world units on the walls.
"""

from game.config.record import record

WINDOW_ATLAS = record(
    {
        "size": 512,
        "cell": 8,
        # One band of columns per style: square punched windows, ribbons running along the floor,
        # tall narrow windows, and a curtain wall of large panes.
        "styles": [
            {"window": [2, 2, 6, 6], "lit": 0.18},
            {"window": [0, 3, 8, 6], "lit": 0.2},
            {"window": [3, 1, 5, 7], "lit": 0.15},
            {"window": [1, 1, 7, 7], "lit": 0.22},
        ],
        # Warm lamps mostly, now and then a cold office light or a screen.
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
        # How much the sun shows the atlas: by day lit windows show faintly, dark ones black.
        "glass": [0.25, 0.25, 0.25],
        "halo": 0.3,
        "seed": 4242,
    }
)

# The wall a window cell covers: its width and its height (one floor).
WINDOW_CELL = record({"width": 2.5, "height": 3})

# How far off its wall the windows' quad stands, so the two never fight in depth.
WINDOW_OFFSET = 0.08

# How much of their own colour the windows of a building take (the rest white), over the
# atlas' colours: warm homes, dim offices, neon towers.
WINDOW_TINT = 0.5
