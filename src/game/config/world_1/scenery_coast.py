# Copyright (c) 2026 Renaud Guillon
"""The first two levels of World 1 (WLD-1-01, WLD-1-05).

Reworked at the reviewer's request, 2026-10-26.

Open sea with small green islands and reefs, then a green coast that gives way to meadows, groves
and farmland, its hills each with a rocky face (WLD-1-31). Heights in world units above the sea
level (0). Each section's `seconds` add up to 240 (WLD-1-03).
"""

from game.config.record import merge, record
from game.config.trees import LIVE_TREES
from game.config.world_1.props import WORLD_1_GROUPS, WORLD_1_PROPS, WORLD_1_ROADS

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


G = WORLD_1_GROUPS

# The hills of World 1's land (WLD-1-31, GFX-TERRAIN-19): each with one steep rocky face and a slow
# slope on the other side. The faces look towards +X and a little towards the camera
# (`SCARP_ANGLE`, from +Z): the sun, ahead and to the right, lights them, and the camera, tilted
# forward, sees them. They take `SCARP_FACE` of a crest-to-crest cycle (the back takes the rest),
# and the crests fall to nothing between the hills.
SCARP_ANGLE = 125
SCARP_FACE = 0.06


def scarps(height: float, wavelength: float, warp: float = 0.8) -> Any:
    """Return World 1's hills: `height` at the highest crests, about `wavelength` apart.

    Their lines wander by `warp` wavelengths.
    """
    return record({
        "height": height,
        "wavelength": wavelength,
        "angleDeg": SCARP_ANGLE,
        "warp": warp,
        "face": SCARP_FACE,
        "lowest": 0,
    })


def smooth(base: float, amplitude: float, wavelength: float, octaves: float = 4) -> Any:
    """Return rolling relief: `base` +/- `amplitude`, features about `wavelength` across."""
    return record({
        "base": base,
        "amplitude": amplitude,
        "frequency": 1 / wavelength,
        "octaves": octaves,
        "style": "smooth",
    })


def shore(x: float, amplitude: float, wavelength: float) -> Any:
    """Return the coast where the land starts, along a winding line.

    The sea is on the left (`landSide` 1).
    """
    return record({
        "path": {"x": x, "amplitude": amplitude, "wavelength": wavelength},
        "landSide": 1,
        "width": 240,
        "seabed": -55,
    })


def water(name: str, seconds: float, base: float, amplitude: float) -> Any:
    """Open water: deep sea bed, nothing stands on it but the islands."""
    return record({
        "name": name,
        "seconds": seconds,
        "relief": smooth(base, amplitude, 520, 5),
        "buildingDensity": 0,
        # D-212: woods on the islands' grass (LVL-1-1-07).
        "treeDensity": 1,
        "trees": LIVE_TREES,
        "surface": {"lush": 0.7},
        "groups": [G.fishing],
    })


# The green coast where 1-1 ends and 1-2 begins (WLD-1-08): a sandy shore, then grass
# (LVL-1-1-05).
GREEN_COAST = record({
    "name": "green coast",
    "seconds": 30,
    "relief": smooth(16, 10, 480),
    "scarps": scarps(28, 340),
    "shore": shore(-40, 90, 1800),
    "buildingDensity": 0.5,
    "treeDensity": 1,
    "surface": {"lush": 0.8, "sandy": 0.2},
    "trees": LIVE_TREES,
    "groups": [G.fishing, G.coastHomes],
})


def green(name: str, seconds: float, extra: Any) -> Any:
    """Return the green land: grass all over, its hills, trees and buildings."""
    return merge(
        record({
            "name": name,
            "seconds": seconds,
            "relief": smooth(24, 10, 600),
            "scarps": scarps(36, 340),
            "buildingDensity": 0.5,
            # D-212: woods on the grass (WLD-1-14; its share sets how much: see `FORESTS`).
            "treeDensity": 1,
            "trees": LIVE_TREES,
            "surface": {"lush": 1},
            "groups": [G.villages, G.farms],
        }),
        extra,
    )


# Farmland, where 1-2 ends and 1-3 begins: lower hills, room for the farms.
FARMLAND = green(
    "farmland",
    45,
    {
        "relief": smooth(26, 8, 620),
        "scarps": scarps(24, 360),
        "buildingDensity": 0.6,
        "groups": [G.farms, G.villages],
    },
)

# 1-1, Open sea (LVL-1-1-04): sea almost all the way, small green islands and reefs, a coast at
# the end.
OPEN_SEA = [
    water("open sea", 35, -70, 30),
    water("reefs", 40, -24, 48),
    water("islands", 45, -12, 50),
    water("deep water", 30, -70, 30),
    water("archipelago", 60, -10, 50),
    # The first coast comes in the last 30 s: a green shore with a fishing village, 1-1's only
    # buildings (LVL-1-1-06).
    GREEN_COAST,
]

# 1-2, Green coast (LVL-1-2-04): beaches and bays along a coast road, then meadows, groves and
# farms (LVL-1-2-06), all wooded (LVL-1-2-07).
GREEN_COAST_LEVEL = [
    merge(GREEN_COAST, {"name": "coast road", "seconds": 40}),
    merge(
        GREEN_COAST,
        {
            "name": "bays",
            "seconds": 40,
            "relief": smooth(22, 14, 460),
            "shore": shore(-90, 170, 1500),
            "buildingDensity": 0.55,
            "treeDensity": 1,
            "groups": [G.coastHomes, G.villages],
        },
    ),
    green(
        "coast farms",
        30,
        {
            "relief": smooth(24, 14, 460),
            "shore": shore(-230, 110, 1700),
            "surface": {"lush": 0.9, "sandy": 0.1},
            "groups": [G.coastHomes, G.farms],
        },
    ),
    green("meadows", 45, {"buildingDensity": 0.5, "treeDensity": 1}),
    green(
        "groves",
        40,
        {
            "relief": smooth(30, 16, 480),
            "scarps": scarps(40, 340),
            "buildingDensity": 0.45,
            "treeDensity": 1,
            "groups": [G.farms],
        },
    ),
    FARMLAND,
]

# 1-1 (LVL-1-1-01, LVL-1-1-02): open sea, the first coast in the last 30 s, at World 1's fastest
# ground speed (WLD-1-04); a sea level (LVL-1-1-05) and one main road only (LVL-1-1-06).
LEVEL_1_1 = record({
    "id": "world-1-1",
    "name": "1-1 Open sea",
    "seed": 1101,
    "scrollSpeed": 70,
    "transition": 420,
    "sections": OPEN_SEA,
    "sea": {"level": 0},
    "roads": merge(WORLD_1_ROADS, {"mainRoads": 1}),
    "props": WORLD_1_PROPS,
})

# 1-2 (LVL-1-2-01, LVL-1-2-02): starts on the green coast where 1-1 ended; the sea is gone after
# 110 s (WLD-1-06, LVL-1-2-05).
LEVEL_1_2 = record({
    "id": "world-1-2",
    "name": "1-2 Green coast",
    "seed": 1201,
    "scrollSpeed": 65,
    "transition": 420,
    "sections": GREEN_COAST_LEVEL,
    "sea": {"level": 0},
    "roads": WORLD_1_ROADS,
    "props": WORLD_1_PROPS,
})
