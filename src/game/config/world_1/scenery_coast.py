"""The first two levels of World 1 (P06-R05, reworked at the reviewer's request, 2026-10-26)

Open sea with small green islands and reefs, then a green coast that gives way to meadows, groves
and farmland. Heights in world units above the sea level (0). Each section's `seconds` add up to 240
(P06-R04).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import merge, record
from game.config.world_1.props import WORLD_1_GROUPS, WORLD_1_PROPS, WORLD_1_ROADS

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

G = WORLD_1_GROUPS


def smooth(base: float, amplitude: float, wavelength: float, octaves: float = 4) -> Any:
    """Rolling relief: `base` +/- `amplitude`, features about `wavelength` across."""
    return record(
        {
            "base": base,
            "amplitude": amplitude,
            "frequency": 1 / wavelength,
            "octaves": octaves,
            "style": "smooth",
        }
    )


def shore(x: float, amplitude: float, wavelength: float) -> Any:
    """The coast where the land starts: sea on the left (`landSide` 1) along a winding line."""
    return record(
        {
            "path": {"x": x, "amplitude": amplitude, "wavelength": wavelength},
            "landSide": 1,
            "width": 240,
            "seabed": -55,
        }
    )


def water(name: str, seconds: float, base: float, amplitude: float) -> Any:
    """Open water: deep sea bed, nothing stands on it but the islands, green with palms."""
    return record(
        {
            "name": name,
            "seconds": seconds,
            "relief": smooth(base, amplitude, 520, 5),
            "buildingDensity": 0,
            # D-212: copses on the islands.
            "treeDensity": 0.35,
            "surface": {"lush": 0.7},
            "groups": [G.fishing],
        }
    )


# The green coast where 1-1 ends and 1-2 begins: a sandy shore, then grass.
GREEN_COAST = record(
    {
        "name": "green coast",
        "seconds": 30,
        "relief": smooth(16, 10, 480),
        "shore": shore(-40, 90, 1800),
        "buildingDensity": 0.5,
        "treeDensity": 0.35,
        "surface": {"lush": 0.8, "sandy": 0.2},
        "groups": [G.fishing, G.coastHomes],
    }
)


def green(name: str, seconds: float, extra: Any) -> Any:
    """The green land: grass all over, its trees and buildings."""
    return merge(
        record(
            {
                "name": name,
                "seconds": seconds,
                "relief": smooth(24, 10, 600),
                "buildingDensity": 0.5,
                # D-212: woods here and there.
                "treeDensity": 0.45,
                "surface": {"lush": 1},
                "groups": [G.villages, G.farms],
            }
        ),
        extra,
    )


# Farmland, where 1-2 ends and 1-3 begins.
FARMLAND = green(
    "farmland",
    45,
    {
        "relief": smooth(26, 8, 620),
        "buildingDensity": 0.6,
        "groups": [G.farms, G.villages],
    },
)

# 1-1, Open sea: sea almost all the way, small green islands and reefs, a coast at the end.
OPEN_SEA = [
    water("open sea", 35, -70, 30),
    water("reefs", 40, -24, 48),
    water("islands", 45, -12, 50),
    water("deep water", 30, -70, 30),
    water("archipelago", 60, -10, 50),
    # The first coast comes in the last 30 s: a green shore with a fishing village.
    GREEN_COAST,
]

# 1-2, Green coast: beaches and bays along a coast road, then meadows, groves and farms.
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
            "treeDensity": 0.3,
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
    green("meadows", 45, {"buildingDensity": 0.5, "treeDensity": 0.3}),
    green(
        "groves",
        40,
        {
            "relief": smooth(30, 16, 480),
            "buildingDensity": 0.45,
            "treeDensity": 0.8,
            "groups": [G.farms],
        },
    ),
    FARMLAND,
]

# 1-1 (P06-R05): open sea, the first coast in the last 30 s.
LEVEL_1_1 = record(
    {
        "id": "world-1-1",
        "name": "1-1 Open sea",
        "seed": 1101,
        "scrollSpeed": 70,
        "transition": 420,
        "sections": OPEN_SEA,
        "sea": {"level": 0},
        "roads": merge(WORLD_1_ROADS, {"mainRoads": 1}),
        "props": WORLD_1_PROPS,
    }
)

# 1-2 (P06-R05): starts on the green coast where 1-1 ended; the sea is gone after 110 s.
LEVEL_1_2 = record(
    {
        "id": "world-1-2",
        "name": "1-2 Green coast",
        "seed": 1201,
        "scrollSpeed": 65,
        "transition": 420,
        "sections": GREEN_COAST_LEVEL,
        "sea": {"level": 0},
        "roads": WORLD_1_ROADS,
        "props": WORLD_1_PROPS,
    }
)
