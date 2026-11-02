# Copyright (c) 2026 Renaud Guillon
"""World 2, the Industrial Desert (WLD-2-01, WLD-2-05).

Reworked at the reviewer's request, 2026-10-27.

The five levels are one journey from the deep desert, where World 1 ended, to dense factories, the
industry in its order (WLD-2-09). The changes are slow (WLD-2-08): the sand gives way to concrete
in small steps (WLD-2-07), the sections blend over a long stretch (`TRANSITION`), and each new
building group first comes in mixed with the one before it. Each level starts on the very section
the previous one ended on (WLD-2-10). No sea (WLD-2-06; rivers would be fine, reviewer,
2026-10-27). Each level's `seconds` add up to 300 (WLD-2-03).
"""

from game.config.record import merge, record
from game.config.world_1.scenery_coast import smooth
from game.config.world_2.props import WORLD_2_GROUPS, WORLD_2_PROPS, WORLD_2_ROADS

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


G = WORLD_2_GROUPS

# Sections blend over this many units (GFX-TERRAIN-10): about 15 s of scrolling, World 1's 420
# doubled.
TRANSITION = 900


def dunes(height: float, wavelength: float, angle_deg: float = 60) -> Any:
    """Sand dunes: crests every `wavelength`, `height` high."""
    return record({"height": height, "wavelength": wavelength, "angleDeg": angle_deg, "warp": 0.6})


# Flat ground for towns and plants.
FLAT = smooth(30, 4, 600, 3)
# A dense maze of straight streets, as in World 1's towns and Level Zero's industrial zone.
STREETS = record({"rows": [45, 90], "columns": [50, 110], "links": 0.6})
# Wider blocks of the mining and company towns, and of the suburbs.
SUBURB_STREETS = record({"rows": [60, 110], "columns": [70, 130], "links": 0.55})


def section(name: str, seconds: float, extra: Any) -> Any:
    """Return a section of World 2: sand and desert outposts, with `extra` set over the defaults."""
    return merge(
        record({
            "name": name,
            "seconds": seconds,
            "relief": smooth(28, 10, 520),
            "buildingDensity": 0.6,
            "treeDensity": 0,
            "surface": {"sandy": 1},
            "groups": [G.outposts],
        }),
        extra,
    )


# The first mines, where 2-1 ends and 2-2 begins.
PROSPECT_MINES = section(
    "prospect mines",
    30,
    {
        "relief": smooth(30, 10, 520, 3),
        "buildingDensity": 1,
        "surface": {"sandy": 0.8, "paved": 0.05},
        "groups": [G.outposts, G.mines],
    },
)

# The first oil wells among the last mines, where 2-2 ends and 2-3 begins.
OIL_EDGE = section(
    "oil edge",
    35,
    {
        "relief": smooth(28, 5, 600, 3),
        "buildingDensity": 1,
        "treeDensity": 0,
        "surface": {"sandy": 0.55, "paved": 0.25},
        "groups": [G.oil, G.mines],
    },
)

# Refineries giving way to the first factories, where 2-3 ends and 2-4 begins.
INDUSTRIAL_EDGE = section(
    "industrial edge",
    45,
    {
        "relief": FLAT,
        "buildingDensity": 1,
        "treeDensity": 0,
        "surface": {"sandy": 0.25, "paved": 0.55},
        "streets": STREETS,
        "groups": [G.refinery, G.industrial],
    },
)

# The factory district, where 2-4 ends and 2-5 begins.
FACTORY_DISTRICT = section(
    "factory district",
    55,
    {
        "relief": smooth(32, 3, 600, 3),
        "buildingDensity": 1,
        "treeDensity": 0,
        "surface": {"sandy": 0.1, "paved": 0.78},
        "streets": STREETS,
        "groups": [G.heavyIndustry, G.industrial],
    },
)

# 2-1, Great erg (LVL-2-1-04): from an oasis on the sand World 1 ended on, across great dunes and
# dune fields (LVL-2-1-05), caravan posts and rocky desert, to the first mines in the last 30 s.
# Buildings and roads: LVL-2-1-06.
GREAT_ERG = [
    section(
        "oasis edge",
        40,
        {
            "relief": FLAT,
            "buildingDensity": 0.3,
            "treeDensity": 0,
            "surface": {"sandy": 0.85, "lush": 0.1},
            "groups": [G.desertHomes, G.outposts],
        },
    ),
    section(
        "great dunes",
        50,
        {"dunes": dunes(60, 300), "buildingDensity": 0.3, "treeDensity": 0},
    ),
    section("caravan posts", 45, {"groups": [G.outposts, G.desertHomes]}),
    section(
        "dune field",
        45,
        {"dunes": dunes(45, 240, 70), "buildingDensity": 0.45, "treeDensity": 0},
    ),
    section(
        "rocky desert",
        50,
        {
            "relief": {
                "base": 22,
                "amplitude": 80,
                "frequency": 1 / 500,
                "octaves": 5,
                "style": "ridged",
                "maxHeight": 110,
            },
            "buildingDensity": 0.8,
            "surface": {"sandy": 0.7},
        },
    ),
    section(
        "desert outposts",
        40,
        {
            "relief": smooth(30, 8, 560, 3),
            "buildingDensity": 1,
            "surface": {"sandy": 0.85},
            "groups": [G.outposts, G.desertHomes],
        },
    ),
    PROSPECT_MINES,
]

# Level 2-2, mining mesas (LVL-2-2-04): the mines spread over mesas and along a canyon
# (LVL-2-2-05), a mining town with streets, open pits, then the first oil wells among the
# mines. Buildings and roads: LVL-2-2-06.
MINING_MESAS = [
    merge(PROSPECT_MINES, {"seconds": 40}),
    section(
        "mesa mines",
        50,
        {
            "relief": {
                "base": 30,
                "amplitude": 150,
                "frequency": 1 / 560,
                "octaves": 5,
                "style": "smooth",
                "maxHeight": 100,
            },
            "buildingDensity": 0.9,
            "surface": {"sandy": 0.75, "paved": 0.05},
            "groups": [G.mines, G.outposts],
        },
    ),
    section(
        "canyon",
        35,
        {
            "relief": smooth(95, 22, 380, 5),
            "channel": {
                # Winds over the 16:9 view (D-249: +/-140 when it was +/-195 wide).
                "path": {"x": 0, "amplitude": 250, "wavelength": 1900},
                "halfWidth": 40,
                "wall": 110,
                "floor": 10,
            },
            "buildingDensity": 0.8,
            "surface": {"sandy": 0.7, "paved": 0.05},
            "groups": [G.mines],
        },
    ),
    section(
        "mining town",
        55,
        {
            "relief": FLAT,
            "buildingDensity": 1,
            "treeDensity": 0,
            "surface": {"sandy": 0.6, "paved": 0.2},
            "streets": SUBURB_STREETS,
            "groups": [G.workerHomes, G.mines],
        },
    ),
    section(
        "open pits",
        45,
        {
            "relief": smooth(26, 12, 480, 4),
            "buildingDensity": 1,
            "surface": {"sandy": 0.65, "paved": 0.15},
            "groups": [G.mines, G.outposts],
        },
    ),
    section(
        "first wells",
        40,
        {
            "relief": smooth(28, 6, 560, 3),
            "buildingDensity": 1,
            "treeDensity": 0,
            "surface": {"sandy": 0.6, "paved": 0.2},
            "groups": [G.mines, G.oil],
        },
    ),
    OIL_EDGE,
]

# 2-3, Oil fields (LVL-2-3-04): pumpjacks and tanks, a company town, refineries and tank farms,
# the first factories at the end, on flat, half-paved ground (LVL-2-3-05). Buildings and roads:
# LVL-2-3-06.
OIL_FIELDS = [
    merge(OIL_EDGE, {"seconds": 40}),
    section(
        "oil fields",
        60,
        {
            "relief": smooth(26, 5, 620, 3),
            "buildingDensity": 1,
            "treeDensity": 0,
            "surface": {"sandy": 0.5, "paved": 0.25},
            "groups": [G.oil],
        },
    ),
    section(
        "company town",
        50,
        {
            "relief": FLAT,
            "buildingDensity": 1,
            "treeDensity": 0,
            "surface": {"sandy": 0.4, "paved": 0.4},
            "streets": SUBURB_STREETS,
            "groups": [G.workerHomes, G.oil],
        },
    ),
    section(
        "refineries",
        55,
        {
            "relief": FLAT,
            "buildingDensity": 1,
            "treeDensity": 0,
            "surface": {"sandy": 0.35, "paved": 0.45},
            "groups": [G.refinery, G.oil],
        },
    ),
    section(
        "tank farms",
        50,
        {
            "relief": FLAT,
            "buildingDensity": 1,
            "treeDensity": 0,
            "surface": {"sandy": 0.3, "paved": 0.5},
            "streets": STREETS,
            "groups": [G.refinery],
        },
    ),
    INDUSTRIAL_EDGE,
]

# 2-4, Industrial belt (LVL-2-4-04): workers' suburbs, warehouses and yards, a power plant,
# factory yards, then the factory district, paved with a little sand between the plots
# (LVL-2-4-05). Buildings and roads: LVL-2-4-06.
INDUSTRIAL_BELT = [
    merge(INDUSTRIAL_EDGE, {"seconds": 40}),
    section(
        "workers' suburbs",
        50,
        {
            "relief": FLAT,
            "buildingDensity": 0.6,
            "treeDensity": 0,
            "surface": {"sandy": 0.22, "paved": 0.6},
            "streets": SUBURB_STREETS,
            "groups": [G.workerHomes, G.industrial],
        },
    ),
    section(
        "warehouses",
        55,
        {
            "relief": FLAT,
            "buildingDensity": 0.7,
            "treeDensity": 0,
            "surface": {"sandy": 0.18, "paved": 0.65},
            "streets": STREETS,
            "groups": [G.industrial],
        },
    ),
    section(
        "power plant",
        45,
        {
            "relief": FLAT,
            "buildingDensity": 1,
            "treeDensity": 0,
            "surface": {"sandy": 0.15, "paved": 0.68},
            "streets": STREETS,
            "groups": [G.industrial, G.refinery],
        },
    ),
    section(
        "factory yards",
        55,
        {
            "relief": FLAT,
            "buildingDensity": 1,
            "treeDensity": 0,
            "surface": {"sandy": 0.12, "paved": 0.72},
            "streets": STREETS,
            "groups": [G.industrial, G.heavyIndustry],
        },
    ),
    FACTORY_DISTRICT,
]

# The great works filling every block, where 2-5 ends and World 3 begins.
GREAT_WORKS = section(
    "great works",
    80,
    {
        "relief": smooth(32, 2, 600, 2),
        "buildingDensity": 1,
        "treeDensity": 0,
        "surface": {"paved": 1},
        "streets": STREETS,
        "groups": [G.heavyIndustry],
        # Every part of every block gets a plant or works, side by side, as in Level Zero's city.
        "blocks": {"podiums": [], "podiumHeight": [0, 0], "towers": [16, 16]},
    },
)

# 2-5, Factory district (LVL-2-5-04): foundries, rail yards, heavy industry, then great works
# filling every block to the end (LVL-2-5-05). Buildings and roads: LVL-2-5-06.
FACTORIES = [
    merge(FACTORY_DISTRICT, {"seconds": 40}),
    section(
        "foundries",
        60,
        {
            "relief": smooth(32, 3, 600, 3),
            "buildingDensity": 0.8,
            "treeDensity": 0,
            "surface": {"sandy": 0.08, "paved": 0.82},
            "streets": STREETS,
            "groups": [G.heavyIndustry, G.industrial],
        },
    ),
    section(
        "rail yards",
        50,
        {
            "relief": smooth(32, 2, 600, 2),
            "buildingDensity": 0.85,
            "treeDensity": 0,
            "surface": {"sandy": 0.06, "paved": 0.86},
            "streets": STREETS,
            "groups": [G.industrial],
        },
    ),
    section(
        "heavy industry",
        70,
        {
            "relief": smooth(32, 2, 600, 2),
            "buildingDensity": 1,
            "treeDensity": 0,
            "surface": {"sandy": 0.04, "paved": 0.92},
            "streets": STREETS,
            "groups": [G.heavyIndustry, G.industrial],
        },
    ),
    GREAT_WORKS,
]


def level(meta: list[Any], scroll_speed: float, sections: list[Any]) -> Any:
    """Return a World 2 level from its `[id, name, seed]`, its scroll speed and its sections.

    Each World 2 level has its own scroll speed (WLD-2-04).
    """
    return record({
        "id": meta[0],
        "name": meta[1],
        "seed": meta[2],
        "scrollSpeed": scroll_speed,
        "transition": TRANSITION,
        "sections": sections,
        "roads": WORLD_2_ROADS,
        "props": WORLD_2_PROPS,
    })


# 2-1 (LVL-2-1-01, LVL-2-1-02): the great erg, from an oasis to the first mines.
LEVEL_2_1 = level(["world-2-1", "2-1 Great erg", 2101], 70, GREAT_ERG)
# 2-2 (LVL-2-2-01, LVL-2-2-02): the mining mesas, starting on the mines 2-1 ended on.
LEVEL_2_2 = level(["world-2-2", "2-2 Mining mesas", 2201], 65, MINING_MESAS)
# 2-3 (LVL-2-3-01, LVL-2-3-02): the oil fields, starting on the first wells 2-2 ended on.
LEVEL_2_3 = level(["world-2-3", "2-3 Oil fields", 2301], 60, OIL_FIELDS)
# 2-4 (LVL-2-4-01, LVL-2-4-02): the industrial belt, starting on the refineries' edge 2-3 ended
# on.
LEVEL_2_4 = level(["world-2-4", "2-4 Industrial belt", 2401], 55, INDUSTRIAL_BELT)
# 2-5 (LVL-2-5-01, LVL-2-5-02): the factory district, starting on the factories 2-4 ended on.
LEVEL_2_5 = level(["world-2-5", "2-5 Factory district", 2501], 60, FACTORIES)
