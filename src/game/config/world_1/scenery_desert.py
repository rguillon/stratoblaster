"""The dry levels of World 1 (P06-R05, R06, reworked at the reviewer's request, 2026-10-26)

From the dry grassland 1-3 ended on to sand and rock, dunes, an oasis, a canyon and mesas, then
deeper into the desert, its towns bigger and denser. No factory and no city: they are for other
worlds (reviewer, 2026-10-27). No sea. Each level's `seconds` add up to 240 (P06-R04).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import merge, record
from game.config.world_1.props import PLANTS, WORLD_1_GROUPS, WORLD_1_PROPS, WORLD_1_ROADS
from game.config.world_1.scenery_coast import smooth
from game.config.world_1.scenery_country import DRY_GRASSLAND, TOWN_STREETS

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

G = WORLD_1_GROUPS


def dunes(height: float, wavelength: float, angle_deg: float = 60) -> Any:
    """Sand dunes: crests every `wavelength`, `height` high (P06-R06)."""
    return record({"height": height, "wavelength": wavelength, "angleDeg": angle_deg, "warp": 0.6})


def mesas(top: float) -> Any:
    """Flat-topped mesas: a high relief whose tops are squashed under `top`."""
    return record(
        {
            "base": 30,
            "amplitude": 150,
            "frequency": 1 / 560,
            "octaves": 5,
            "style": "smooth",
            "maxHeight": top,
        }
    )


def desert(name: str, seconds: float, extra: Any) -> Any:
    """A desert section: sand and scrub, with `extra` set over the defaults."""
    return merge(
        record(
            {
                "name": name,
                "seconds": seconds,
                "relief": smooth(28, 12, 520),
                "buildingDensity": 0,
                "treeDensity": 0.35,
                "surface": {"sandy": 1},
                "trees": PLANTS.desert,
                "groups": [G.outposts],
            }
        ),
        extra,
    )


# The outskirts of the desert towns, where 1-4 ends and 1-5 begins: homes and outposts.
DESERT_OUTSKIRTS = desert(
    "desert outskirts",
    30,
    {
        "relief": smooth(30, 8, 560, 3),
        "buildingDensity": 1,
        "treeDensity": 0.45,
        "surface": {"sandy": 0.85},
        "trees": PLANTS.oasis,
        "groups": [G.desertHomes, G.outposts],
    },
)

# 1-4, Dry lands: dry grass and scrub, then sand and rock, dunes, an oasis town, a canyon, mesas
# and a desert town. The bare stretches (rock, dunes, cliffs) are short, so the props keep growing
# in number (P06-R05).
DRY_LANDS = [
    DRY_GRASSLAND,
    desert(
        "scrubland villages",
        40,
        {
            "relief": smooth(30, 14, 520),
            "buildingDensity": 1,
            "treeDensity": 0.6,
            "surface": {"sandy": 0.35},
            "trees": PLANTS.dry,
            "groups": [G.desertHomes, G.outposts],
        },
    ),
    desert(
        "sand and rock",
        20,
        {
            "relief": {
                "base": 20,
                "amplitude": 90,
                "frequency": 1 / 520,
                "octaves": 5,
                "style": "ridged",
                "maxHeight": 120,
            },
            "buildingDensity": 0.6,
        },
    ),
    desert(
        "dunes",
        20,
        {"dunes": dunes(50, 260), "buildingDensity": 0.45, "treeDensity": 0.2},
    ),
    desert(
        "oasis town",
        45,
        {
            "buildingDensity": 1,
            "treeDensity": 0.7,
            "surface": {"sandy": 0.75, "lush": 0.25},
            "streets": TOWN_STREETS,
            "trees": PLANTS.oasis,
            "groups": [G.desertHomes],
        },
    ),
    desert(
        "canyon",
        20,
        {
            "relief": smooth(95, 22, 380, 5),
            "channel": {
                "path": {"x": 0, "amplitude": 140, "wavelength": 1900},
                "halfWidth": 40,
                "wall": 110,
                "floor": 10,
            },
            "buildingDensity": 0.5,
        },
    ),
    desert(
        "mesas",
        20,
        {
            "relief": mesas(100),
            "buildingDensity": 0.9,
        },
    ),
    desert(
        "desert town",
        25,
        {
            "relief": smooth(30, 4, 600, 3),
            "buildingDensity": 1,
            "treeDensity": 0.45,
            "surface": {"sandy": 0.8, "paved": 0.15},
            "streets": TOWN_STREETS,
            "trees": PLANTS.town,
            "groups": [G.desertHomes],
        },
    ),
    merge(DESERT_OUTSKIRTS, {"seconds": 20}),
]

# 1-5, Deep desert (reviewer, 2026-10-27: the factories and the city are for other worlds): the
# desert outskirts, great dunes, oasis villages, a rocky pass, then desert towns, bigger and denser,
# on the sand to the end.
DEEP_DESERT = [
    DESERT_OUTSKIRTS,
    desert(
        "great dunes",
        25,
        {"dunes": dunes(60, 300), "buildingDensity": 0.45, "treeDensity": 0.2},
    ),
    desert(
        "oasis villages",
        40,
        {
            "buildingDensity": 1,
            "treeDensity": 0.7,
            "surface": {"sandy": 0.7, "lush": 0.3},
            "streets": TOWN_STREETS,
            "trees": PLANTS.oasis,
            "groups": [G.desertHomes, G.outposts],
        },
    ),
    desert(
        "rocky pass",
        20,
        {
            "relief": smooth(60, 30, 420, 5),
            "buildingDensity": 0.7,
            "groups": [G.outposts],
        },
    ),
    desert(
        "desert towns",
        55,
        {
            "relief": smooth(28, 6, 560, 3),
            "buildingDensity": 1,
            "treeDensity": 0.45,
            "surface": {"sandy": 0.85, "paved": 0.1},
            "streets": TOWN_STREETS,
            "trees": PLANTS.town,
            "groups": [G.desertHomes, G.outposts],
        },
    ),
    desert(
        "great oasis town",
        70,
        {
            "relief": smooth(30, 4, 600, 3),
            "buildingDensity": 1,
            "treeDensity": 0.6,
            "surface": {"sandy": 0.8, "lush": 0.1, "paved": 0.1},
            "streets": record({"rows": [45, 90], "columns": [50, 110], "links": 0.6}),
            "trees": PLANTS.oasis,
            "groups": [G.desertHomes],
        },
    ),
]


def level(level_id: str, name: str, seed: float, sections: list[Any]) -> Any:
    """A World 1 desert level: its sections on the World 1 roads and props."""
    return record(
        {
            "id": level_id,
            "name": name,
            "seed": seed,
            "scrollSpeed": 60,
            "transition": 420,
            "sections": sections,
            "roads": WORLD_1_ROADS,
            "props": WORLD_1_PROPS,
        }
    )


# 1-4 (P06-R05): the dry lands, starting on the dry grassland 1-3 ended on.
LEVEL_1_4 = level("world-1-4", "1-4 Dry lands", 1401, DRY_LANDS)
# 1-5: the deep desert, starting on the desert outskirts 1-4 ended on.
LEVEL_1_5 = level("world-1-5", "1-5 Deep desert", 1501, DEEP_DESERT)
