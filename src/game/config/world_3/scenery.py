"""World 3 (P09-R03; reworked at the reviewer's request, 2026-10-27), ported from
`config/world-3/scenery.ts`.

The five levels are one journey from the great works World 2 ended on, along canals and docks,
through the workers' quarters and the terraces, to garden suburbs and villages of small houses (no
tower). The changes are slow, as in World 2: the concrete gives way to grass in small steps, the
sections blend over World 2's long stretch (`TRANSITION`), and each new building group first comes
in mixed with the one before it. Each level starts on the very section the previous one ended on. No
water (reviewer, 2026-10-28): no sea, canal, river or pond. Each level's `seconds` add up to 300
(P09-R02).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import merge, record
from game.config.world_1.scenery_coast import smooth
from game.config.world_2.scenery import GREAT_WORKS, TRANSITION
from game.config.world_3.props import TOWN_PLANTS, WORLD_3_GROUPS, WORLD_3_PROPS, WORLD_3_ROADS

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

PL = TOWN_PLANTS
G = WORLD_3_GROUPS

# The river through World 4's suburbs and villages, between grassy banks.
RIVER_PATH = record({"x": -40, "amplitude": 120, "wavelength": 2400})


def river(half_width: float) -> Any:
    """The river of `half_width` at its bed, between grassy banks."""
    return record({"path": RIVER_PATH, "halfWidth": half_width, "wall": 45, "floor": -8})


# Ponds among the gardens where World 4 begins.
PONDS = record({"spacing": 260, "chance": 0.4, "radius": [22, 45], "level": -5, "edge": 16})

# Flat ground of the factories, the yards and the streets.
FLAT = smooth(32, 2, 600, 2)
# Gently rolling ground of the suburbs and the villages.
ROLLING = smooth(30, 6, 560, 3)
# A dense maze of straight streets, as in World 2's factories.
STREETS = record({"rows": [45, 90], "columns": [50, 110], "links": 0.6})
# Narrower, longer blocks of the terraced streets.
TERRACE_STREETS = record({"rows": [33, 56], "columns": [38, 76], "links": 0.6})
# Blocks of the suburbs, a house on each plot.
SUBURB_STREETS = record({"rows": [40, 70], "columns": [50, 95], "links": 0.6})
# The closer blocks of the river suburbs of 3-4.
GARDEN_SUBURB_STREETS = record({"rows": [36, 62], "columns": [46, 88], "links": 0.6})
# The small blocks of the leafy avenues of 3-4.
AVENUE_STREETS = record({"rows": [36, 62], "columns": [40, 78], "links": 0.65})
# Small blocks of the garden villages: lanes between the gardens.
VILLAGE_STREETS = record({"rows": [40, 70], "columns": [45, 90], "links": 0.65})
# The lanes of the last garden villages, closest of all.
LANES = record({"rows": [35, 60], "columns": [40, 80], "links": 0.7})


def section(name: str, seconds: float, extra: Any) -> Any:
    """A section of World 3: factories and yards, with `extra` set over the defaults."""
    return merge(
        record(
            {
                "name": name,
                "seconds": seconds,
                "relief": FLAT,
                "buildingDensity": 1,
                "treeDensity": 0.1,
                "surface": {"paved": 0.9},
                "streets": STREETS,
                "trees": PL["industry"],
                "groups": [G.industrial],
            }
        ),
        extra,
    )


# Workshops along the canal, where 3-1 ends and 3-2 begins.
CANAL_WORKSHOPS = section(
    "canal workshops",
    50,
    {
        "treeDensity": 0.12,
        "surface": {"paved": 0.85, "lush": 0.04},
        "trees": PL["yards"],
        "groups": [G.workshops, G.industrial],
    },
)

# The first workers' flats among the workshops, where 3-2 ends and 3-3 begins.
FIRST_FLATS = section(
    "first flats",
    50,
    {
        "treeDensity": 0.22,
        "surface": {"paved": 0.68, "lush": 0.12},
        "trees": PL["streets"],
        "groups": [G.workerFlats, G.workshops],
    },
)

# Terraces giving way to the first houses, where 3-3 ends and 3-4 begins.
SUBURB_EDGE = section(
    "suburb edge",
    45,
    {
        "relief": ROLLING,
        "treeDensity": 0.45,
        "surface": {"paved": 0.42, "lush": 0.4},
        "streets": SUBURB_STREETS,
        "trees": PL["streets"],
        "groups": [G.residences],
    },
)

# Houses giving way to the garden villages, where 3-4 ends and 3-5 begins.
VILLAGE_EDGE = section(
    "village edge",
    45,
    {
        "relief": ROLLING,
        "treeDensity": 0.6,
        "surface": {"paved": 0.2, "lush": 0.65},
        "streets": SUBURB_STREETS,
        "trees": PL["gardens"],
        "groups": [G.residences, G.villages],
    },
)

# 3-1, Canal works: from the great works 2-5 ended on, foundries along a canal, rail yards, the
# canal docks and factory yards, to the first workshops.
CANAL_WORKS = [
    merge(GREAT_WORKS, {"seconds": 40, "groups": [G.heavyIndustry]}),
    section(
        "foundry canal",
        55,
        {
            "buildingDensity": 0.6,
            "treeDensity": 0.04,
            "surface": {"paved": 0.96},
            "groups": [G.heavyIndustry, G.industrial],
        },
    ),
    section(
        "rail yards",
        50,
        {
            "buildingDensity": 0.6,
            "treeDensity": 0.06,
            "surface": {"paved": 0.94},
        },
    ),
    section(
        "canal docks",
        55,
        {
            "buildingDensity": 0.9,
            "treeDensity": 0.06,
            "surface": {"paved": 0.92},
            "groups": [G.docks, G.industrial],
        },
    ),
    section(
        "factory yards",
        50,
        {
            "treeDensity": 0.08,
            "surface": {"paved": 0.88, "lush": 0.02},
            "trees": PL["yards"],
            "groups": [G.industrial, G.docks],
        },
    ),
    CANAL_WORKSHOPS,
]

# 3-2, Docklands: warehouses on the canal docks, the workshops' streets, old mills, then the first
# workers' flats.
DOCKLANDS = [
    merge(CANAL_WORKSHOPS, {"seconds": 40}),
    section(
        "warehouse docks",
        55,
        {
            "buildingDensity": 0.85,
            "treeDensity": 0.1,
            "surface": {"paved": 0.84, "lush": 0.04},
            "trees": PL["yards"],
            "groups": [G.docks, G.workshops],
        },
    ),
    section(
        "workshop streets",
        55,
        {
            "treeDensity": 0.14,
            "surface": {"paved": 0.8, "lush": 0.06},
            "trees": PL["yards"],
            "groups": [G.workshops],
        },
    ),
    section(
        "old mills",
        50,
        {
            "treeDensity": 0.16,
            "surface": {"paved": 0.76, "lush": 0.08},
            "trees": PL["yards"],
            "groups": [G.workshops, G.industrial],
        },
    ),
    section(
        "workers' blocks",
        50,
        {
            "treeDensity": 0.18,
            "surface": {"paved": 0.72, "lush": 0.1},
            "trees": PL["streets"],
            "groups": [G.workshops, G.workerFlats],
        },
    ),
    FIRST_FLATS,
]

# 3-3, Workers' quarter: blocks of flats, terraced streets, a park along the canal, brick terraces,
# then the first houses by the river.
WORKERS_QUARTER = [
    merge(FIRST_FLATS, {"seconds": 40}),
    section(
        "workers' flats",
        60,
        {
            "treeDensity": 0.25,
            "surface": {"paved": 0.64, "lush": 0.15},
            "trees": PL["streets"],
            "groups": [G.workerFlats],
        },
    ),
    section(
        "terraced streets",
        55,
        {
            "treeDensity": 0.28,
            "surface": {"paved": 0.6, "lush": 0.18},
            "streets": TERRACE_STREETS,
            "trees": PL["streets"],
            "groups": [G.residences, G.workerFlats],
        },
    ),
    section(
        "canal park",
        45,
        {
            "buildingDensity": 1,
            "treeDensity": 0.55,
            "surface": {"paved": 0.4, "lush": 0.45},
            "trees": PL["parks"],
            "groups": [G.residences],
        },
    ),
    section(
        "brick terraces",
        55,
        {
            "treeDensity": 0.35,
            "surface": {"paved": 0.5, "lush": 0.3},
            "streets": TERRACE_STREETS,
            "trees": PL["streets"],
            "groups": [G.residences],
        },
    ),
    SUBURB_EDGE,
]

# 3-4, Suburbs: garden suburbs, houses along the river, a park, leafy avenues, then the first garden
# villages.
SUBURBS = [
    merge(SUBURB_EDGE, {"seconds": 40}),
    section(
        "garden suburbs",
        60,
        {
            "relief": ROLLING,
            "treeDensity": 0.5,
            "surface": {"paved": 0.36, "lush": 0.46},
            "streets": SUBURB_STREETS,
            "trees": PL["streets"],
            "groups": [G.residences],
        },
    ),
    section(
        "river suburbs",
        55,
        {
            "relief": ROLLING,
            "treeDensity": 0.55,
            "surface": {"paved": 0.3, "lush": 0.52},
            "streets": GARDEN_SUBURB_STREETS,
            "trees": PL["gardens"],
            "groups": [G.residences],
        },
    ),
    section(
        "town park",
        45,
        {
            "relief": ROLLING,
            "buildingDensity": 1,
            "treeDensity": 0.7,
            "surface": {"paved": 0.2, "lush": 0.7},
            "trees": PL["parks"],
            "groups": [G.residences],
        },
    ),
    section(
        "leafy avenues",
        55,
        {
            "relief": ROLLING,
            "treeDensity": 0.55,
            "surface": {"paved": 0.26, "lush": 0.58},
            "streets": AVENUE_STREETS,
            "trees": PL["gardens"],
            "groups": [G.residences],
        },
    ),
    VILLAGE_EDGE,
]

# The garden villages of small houses, where 3-5 ends and World 4 begins.
GARDEN_VILLAGE_END = section(
    "garden villages",
    95,
    {
        "relief": ROLLING,
        "treeDensity": 0.7,
        "surface": {"paved": 0.1, "lush": 0.82},
        "streets": LANES,
        "trees": PL["gardens"],
        "groups": [G.villages],
    },
)

# 3-5, Garden villages: a village green with its ponds, allotments and greenhouses, cottages along
# the river, then garden villages of small houses to the end.
GARDEN_VILLAGES = [
    merge(VILLAGE_EDGE, {"seconds": 40}),
    section(
        "village green",
        60,
        {
            "relief": ROLLING,
            "treeDensity": 0.65,
            "surface": {"paved": 0.16, "lush": 0.72},
            "streets": VILLAGE_STREETS,
            "trees": PL["gardens"],
            "groups": [G.villages, G.residences],
        },
    ),
    section(
        "allotments",
        50,
        {
            "relief": ROLLING,
            "treeDensity": 0.6,
            "surface": {"paved": 0.12, "lush": 0.78},
            "streets": VILLAGE_STREETS,
            "trees": PL["gardens"],
            "groups": [G.villages],
        },
    ),
    section(
        "riverside cottages",
        55,
        {
            "relief": ROLLING,
            "treeDensity": 0.65,
            "surface": {"paved": 0.12, "lush": 0.78},
            "streets": VILLAGE_STREETS,
            "trees": PL["parks"],
            "groups": [G.villages],
        },
    ),
    GARDEN_VILLAGE_END,
]


def level(meta: list[Any], scroll_speed: float, sections: list[Any]) -> Any:
    """A World 3 level: its `[id, name, seed]`, its scroll speed and its sections."""
    return record(
        {
            "id": meta[0],
            "name": meta[1],
            "seed": meta[2],
            "scrollSpeed": scroll_speed,
            "transition": TRANSITION,
            "sections": sections,
            "roads": WORLD_3_ROADS,
            "props": WORLD_3_PROPS,
        }
    )


# 3-1 (P09-R03): the canal works, from the great works 2-5 ended on.
LEVEL_3_1 = level(["world-3-1", "3-1 Canal works", 3101], 70, CANAL_WORKS)
# 3-2: the docklands, starting on the canal workshops 3-1 ended on.
LEVEL_3_2 = level(["world-3-2", "3-2 Docklands", 3201], 60, DOCKLANDS)
# 3-3: the workers' quarter, starting on the first flats 3-2 ended on.
LEVEL_3_3 = level(["world-3-3", "3-3 Workers' quarter", 3301], 55, WORKERS_QUARTER)
# 3-4: the suburbs, starting on the suburb edge 3-3 ended on.
LEVEL_3_4 = level(["world-3-4", "3-4 Suburbs", 3401], 60, SUBURBS)
# 3-5: the garden villages, starting on the village edge 3-4 ended on.
LEVEL_3_5 = level(["world-3-5", "3-5 Garden villages", 3501], 60, GARDEN_VILLAGES)
